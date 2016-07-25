from itertools import chain, izip
from os import listdir, chdir
import json
from pprint import pprint
import time

class Reader:
    """Iterator protocol that yields lines from the file specified in filepath.  Creates an iterable object."""

    def __init__(self, filepath, delim_type, line_limit=None):
        """Opens the file and sets the line_gen"""
        self.filepath = filepath
        self.delim_type = delim_type
        self.line_limit = line_limit
        self.current = 0

        self.f = self.open_file()

    def open_file(self):
        """Opens the file specified in 'filepath'"""
        return open(self.filepath, 'r')

    def __iter__(self):
        """Allows you to iterate over self.line_gen using iter"""
        return self

    def next(self):
        """Generator that will yield lines in the file"""
        if self.line_limit:
            for line in self.f:
                if self.current > self.line_limit:
                    raise StopIteration
                else:
                    self.current += 1
                    return line.strip().split(self.delim_type)
        else:
            for line in self.f:
                line = line.strip().split(self.delim_type)
                if line is not None:
                    return line
                else:
                    raise StopIteration

    def __del__(self):
        """Closes and deletes file self.f"""
        self.f.close()
        del self.f


class Manipulator:
    """Class to do manipulation on lines fed in from a generator.  Includes wide to long and calculating
    BEH statistics, and more.  Specifically designed to work with class Reader
    """
    def __init__(self, generator, long=True, SIC=False):
        """ Set object attributes and read and format based on line 1.
        ---------------
        Keyword Arguments:
        generator:  A generator of list data in wide format to be transferred to long.  Successful transformation
        requires correct data formatting and column titles as the first thing created by the generator.
        sic:  Boolean to indicate whether this is the SIC file, which needs special treatment

        """
        self.decades = ('0', '1', '9') #decade in YYYY date format
        self.generator = generator
        self.SIC = SIC

        self.line1_noformat = self.set_attributes()  # Line 1 as read from the original file
        self.line1 = self.format_line1(self.line1_noformat) #Line 1 post formatting (changing columns for w2l)

        if self.SIC: # only for SIC files
            self.time_indices = [self.line1_noformat.index(i) for i in self.line1_noformat if i[-2] in self.decades]
            self.sic8_index = self.line1_noformat.index('SIC8')

    def splitlist(self, numsplits, l, ratings):
        """
        Split List into sub-lists of equal size whilst preserving order
        ------------
        Keyword Arguments:
        numsplits:  number of sublists to return
        list:  original list to be split
        ratings: is the file the wonky ordering of 'ratings', very specific to this type
        """
        listlen = len(l)
        if not ratings:
            for i in range(0, listlen, numsplits):
                yield l[i:i + numsplits]

        else:
            inc = listlen / numsplits  # num to increment by
            k = inc
            for j in range(0, inc):
                indices = [j, j + k, j + k + 1]
                k = k + 1
                yield [l[j] for j in indices]

    def remove_duplicates(self, seq):
        """Efficient order-preserving method of removing duplicates from an iterable """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def BEH(self, line):
        """ Calculate BEH statistics.  BEH statistics include:
        common:  most common SIC code across all years
        BEH_LargestPercent:  highest percent of years that any single SIC code was used
        BEH_SIC:  If BEH_LargestPercent >= 75, BEH_SIC = Common.  Otherwise, BEH_SIC = most recent SIC
        ---------
        Keyword Arguments:
        line: Data line that would be found within the SIC NETS file

        """
        list_sic = [line[i] for i in self.time_indices] # New variable with non-time removed from the list
        list_sic = filter(None, list_sic)
        common = max(set(list_sic), key=list_sic.count)  # Most common SIC
        BEH_LargestPercent = round((float(list_sic.count(common)) / len(list_sic) * 100), 2)

        if BEH_LargestPercent >= 75:
            BEH_SIC = common
        else:
            BEH_SIC = line[self.sic8_index]

        return [common, str(BEH_LargestPercent), BEH_SIC]

    def format_line1(self, line1):
        """Read and format first line and return it.  You must pass the first line as an argument.
        -------------
        Returns: Formatted First Line.
        """
        colnames = list(chain.from_iterable([[line1[0]], self.yearvars, self.nonyears]))
        colnames.insert(1, 'Year')  # add 'Year" as second element
        return colnames

    def set_attributes(self):
        """Set all attributes to be used in later manipulation functions"""
        line1 = next(self.generator) #get the first line from the generator
        if self.SIC:
            line1 = line1 + ['Common_SIC', 'BEH_LargestPercent', 'BEH_SIC', 'Overall_Class', 'Class_Here']

        self.preyears, self.nonyears = [x for x in line1[1:] if x[-2] in self.decades], \
                             [x for x in line1[1:] if x[-2] not in self.decades]
        self.yearvars = self.remove_duplicates([x[:-2] for x in self.preyears])
        self.year_indices = [line1.index(x) for x in self.preyears]
        self.nonyear_indices = [line1.index(x) for x in self.nonyears]
        allyears = ['19' + h[-2:] if h[-2] == '9' else '20' + h[-2:] for h in self.preyears]  # convert to 'YYYY' format
        self.unique_years = self.remove_duplicates(allyears)

        # Do we need to deal with the funky formatting in the ratings table?
        if len(allyears) > 24 and allyears[0] != allyears[1]:
            self.ratings = True
        else:
            self.ratings = False

        self.num_all_years = len(allyears)  # number of total year-based columns
        self.numw2l = self.num_all_years / len(self.unique_years)  # number of vars to go from wide to long

        return line1

    def wide_to_long_single(self, line, SIC=False):
        """  Convert a single line from the wide to long format.  Time variables are inferred based on the class
        attribute self.year_indices.  Returns a nested list of the lines created from the single argument "line".
        -----------
        Keyword Arguments:
        line: The line of wide data to be transformed into the long format.

        """
        if SIC:  # Calculate and add the BEH attributes if this is a SIC file
            line = line + self.BEH(line)
        try:
            key, time, nontime = line[0], [line[i] for i in self.year_indices], [
                [line[i] for i in self.nonyear_indices]] * self.num_all_years  # separate key from the rest of the line
        except IndexError:  # caused by a line having only a key or not enough values, pad it with empty vals
            padding = ["" for i in range(len(self.line1_noformat) - len(line))]
            padded = line + padding
            key, time, nontime = padded[0], [padded[i] for i in self.year_indices], [
                [padded[i] for i in self.nonyear_indices]] * self.num_all_years

        timesplit = self.splitlist(self.numw2l, time, self.ratings)  # split into equal lists

        line_list = []
        for year, timevals, nontimevals in zip(self.unique_years, timesplit, nontime):
            if not any(timevals):  # if the long to wide values are not empty
                continue
            else:
                line_list.append([key] + [year] + timevals + nontimevals)

        return line_list

    def wide_to_long_all(self):
        """
        Perform self.wide_to_long() on all lines listed in self.generator, returns a new generator for the transformed
        lines
        """
        for line in self.generator:
                line_list = self.wide_to_long_single(line)
                for single_line in line_list:
                    yield single_line


class Classifier:
    def __init__(self, config_file, delim = ','):
        """Read JSON config file as global and reformat SIC ranges"""
        self.config_file = config_file
        self.delim = delim

        self.all_config = self.read_config_json(self.config_file)
        self.make_range()

    def read_config_json(self, config_filepath):
        """Reads JSON config file for classification into a dict and returns it
        -----------
        Keyword Arguments:
        config_filepath: Full file path to the JSON config file
        """
        with open(config_filepath) as f:
            config_dict = json.load(f)
        return config_dict

    def make_range(self):
        """SIC ranges in all_config are originally ranges in form such as [1,5,7,11]
        make_range splits them up into a list of tuples, such as [(1,5),(7,11)] where each tuple indicates an inclusive
        range.  Function to_zip(iterable) is nested, where iterable is a list with an even number of items.
        """
        def to_zip(iterable):
            #iterable = [int(i) for i in iterable if i]  #convert the iterable to int if it isn't empty str
            return zip(iterable[0::2], iterable[1::2])

        for key, _ in self.all_config.iteritems():
            try:
                self.all_config[key]['sic_range'] = to_zip(self.all_config[key]['sic_range'])
                self.all_config[key]['sic_range_2'] = to_zip(self.all_config[key]['sic_range_2'])
            except KeyError:
                continue

    def is_class(self, config_key, name, sic, emp, sales):
        """
        Returns True if the business described belongs to the class described in config_key, returns False otherwise.
        -------
        Keyword Arguments:
        config_key: key that indicates what type of business is to be checked in self.all_config
        name: name of the business to be classified
        sic: SIC code of the business to be classified
        emp: Number of employees of the business to be classified
        sales:  Yearly sales yield of the business to be classified
        """
        local_config = self.all_config[config_key]
        condit_code = local_config['conditional']

        try:
            sic = int(sic)
        except ValueError:
            sic = None
        try:
            emp = int(emp)
        except ValueError:
            emp = None
        try:
            sales = int(sales)
        except ValueError:
            sales = None

        try:
            name_bool = False
            for config_name in local_config['name']:
                name_bool = config_name.lower() in name.lower()
                if name_bool:
                    break
        except KeyError:
            pass

        try:
            sic_exclusive_bool = False
            sic_exclusive_bool = str(sic) in local_config['sic_exclusive']
        except KeyError:
            pass

        try:
            sic_range_bool = False
            for num_range in local_config['sic_range']:
                if int(num_range[0]) <= sic <= int(num_range[1]):
                    sic_range_bool = True
        except KeyError:
            pass

        try:
            sic_range_2_bool = False
            for num_range_2 in local_config['sic_range_2']:
                if int(num_range_2[0]) <= sic <= int(num_range_2[1]):
                    sic_range_2_bool = True
        except KeyError:
            pass

        try:
            emp_bool = False
            if local_config['emp'][0] == 'g':
                emp_bool = emp > int(local_config['emp'][1:])
            else:
                emp_bool = emp < int(local_config['emp'][1:])
        except KeyError:
            pass

        try:
            sales_bool = False
            if local_config['sales'][0] == 'g':
                sales_bool = sales > int(local_config['sales'][1:])
            else:
                sales_bool = sales < int(local_config['sales'][1:])
        except KeyError:
            pass

        if condit_code == 1:
            if name_bool:
                return True
            else:
                return False
        elif condit_code == 2:
            if sic_exclusive_bool or (sic_range_bool and name_bool):
                return True
            else:
                return False
        elif condit_code == 3:
            if sic_range_bool:
                return True
            else:
                return False
        elif condit_code == 4:
            if sic_exclusive_bool and sic_range_bool:
                return True
            else:
                return False
        elif condit_code == 5:
            if sic_range_bool and emp_bool:
                return True
            else:
                return False
        elif condit_code == 6:
            if sic_range_bool and (sales_bool or emp_bool):
                return True
            else:
                return False
        elif condit_code == 7:
            if sic_range_bool or (sic_range_2_bool and name_bool):
                return True
            else:
                return False
        elif condit_code == 8:
            if sic_exclusive_bool:
                return True
            else:
                return False
        elif condit_code == 9:
            if sic_exclusive_bool or name_bool:
                return True
            else:
                return False

    def classify(self, name, sic, emp, sales):
        """  Classify a business into a category defined in self.all_config.  If no category matches, return 'not'.
        --------------
        Keyword Arguments:
        name: name of the business to be classified
        sic: SIC code of the business to be classified
        emp: Number of employees of the business to be classified
        sales:  Yearly sales yield of the business to be classified
        """
        true_keys = []
        for key, _ in self.all_config.iteritems():
            if self.is_class(key, name, sic, emp, sales):
                true_keys.append(key)
            else:
                continue

        if not true_keys:
            return 'not'
        else:
            return ' ; '.join(true_keys)


    def classify_all(self, class_atts_iterable):
        """ Return a generator that classifies each of the business in class_atts_iterable
        -----------
        Keyword Arguments:
        class_atts_iterable: Generator or nested list of business info necessary for classification.  Each list nested
        in the iterable should contain: [name, sic, emp, sales]
        """
        for business in class_atts_iterable:
            try:
                name, sic, emp, sales = business
            except ValueError:
                print("Didn't provide all necessary variables for classification\n"
                      "Variables Needed:\n"
                      "name, sic, emp, sales")
            yield self.classify(name, sic, emp, sales)


class Writer:
    def __init__(self, filepath, delim_type, generator=None):
        """Set object attributes and open the file for writing"""
        self.filepath = filepath
        self.delim_type = delim_type
        self.generator = generator

        self.f = open(self.filepath, 'w')  # Open the file for writing

    def write_line(self, data_list):
        """Write a single line to the file self.f
        -------
        Keyword Arguments:
        data_list: list of data to be converted to str and written
        """
        self.f.write(self.delim_type.join(data_list) + '%s \n' % self.delim_type)

    def write_all(self):
        """Perform self.write on all lines in self.generator"""
        if self.generator:
            for line in self.generator:
                self.write_line(line)
        else:
            print('No generator present for this Writer instance.')

    def __del__(self):
        """Close and delete the file self.f"""
        self.f.close()
        del(self.f)

if __name__ == '__main__':
    t0 = time.time()
    # Read and config paths
    json_config = r'C:\Users\jc4673\Documents\Columbia\nets_wrangle\json_config.json'
    sic = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"
    emp = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Emp.txt"
    sales = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Sales.txt"
    company = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"
    delim = '\t'

    #  Write Paths
    sic_out = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\SIC_transformed.txt"
    emp_out = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\Emp_transformed.txt"
    sales_out = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\Sales_transformed.txt"

    # Create Readers
    limit = 10**3
    read_sic = Reader(sic, delim, line_limit=limit)
    read_emp = Reader(emp, delim, line_limit=limit)
    read_sales = Reader(sales, delim, line_limit=limit)
    read_company = Reader(company, delim, line_limit=limit)
    classifier = Classifier(json_config, delim=delim)

    # Create manipulators and define indices of interest for classification
    manip_sic = Manipulator(read_sic, SIC=True)

    manip_emp = Manipulator(read_emp, SIC=False)
    emp_index = manip_emp.line1_noformat.index('EmpHere')

    manip_sales = Manipulator(read_sales, SIC=False)
    sales_index = manip_sales.line1_noformat.index('SalesHere')

    company_index = next(read_company).index('Company')

    # Create writers
    write_sic = Writer(sic_out, delim_type=delim)
    write_sales = Writer(sales_out, delim_type=delim)
    write_emp = Writer(emp_out, delim_type=delim)

    # Write the first line
    write_sic.write_line(manip_sic.line1)
    write_sales.write_line(manip_sales.line1)
    write_emp.write_line(manip_emp.line1)

    sic_here_index = manip_sic.line1.index('SIC')
    emp_here_index = manip_emp.line1.index('Emp')
    sales_here_index = manip_sales.line1.index('Sales')

    for sic, emp, sales, company in izip(manip_sic.generator, manip_emp.generator, manip_sales.generator, read_company):

        sic += manip_sic.BEH(sic)
        try:
            classification = classifier.classify(company[company_index], sic[-1], emp[emp_index], sales[sales_index])
        except IndexError:
            classification = 'error'

        sic.append(classification)
        long_sic = manip_sic.wide_to_long_single(sic + ['Filler'])  #add extra empty at the end as filler for ClassHere
        long_emp = manip_emp.wide_to_long_single(emp)
        long_sales = manip_sales.wide_to_long_single(sales)

        for sic_long, emp_long, sales_long in zip(long_sic, long_emp, long_sales):
            sic_long[-1] = (classifier.classify(company[company_index], sic_long[sic_here_index],
                                                emp_long[emp_here_index], sales[sales_here_index]))

            write_sic.write_line(sic_long)
            write_emp.write_line(emp_long)
            write_sales.write_line(sales_long)

    del(read_company)
    del(read_emp)
    del(read_sales)
    del(read_sic)
    del(write_sic)
    del(write_emp)
    del(write_sales)

    t1 = time.time()
    print(t1-t0)
