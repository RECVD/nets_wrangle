from itertools import chain
from os import listdir, chdir
import json
from pprint import pprint


class Reader:
    """Iterator protocol that yields lines from the file specified in filepath.  Creates an iterable object."""

    def __init__(self, filepath, delim_type, line_limit=0):
        """Opens the file and sets the line_gen"""
        self.filepath = filepath
        self.delim_type = delim_type
        self.line_limit = line_limit
        self.current = 0

        self.f = self.open_file()
        # self.line_gen = self.read_all()  # create line generator

    def open_file(self):
        """Opens the file specified in 'filepath'"""
        return open(self.filepath, 'r')

    def __iter__(self):
        """Allows you to iterate over self.line_gen using iter"""
        return self

    def next(self):
        """Generator that will yield lines in the file"""
        for line in self.f:
            if self.current > self.line_limit:
                raise StopIteration
            else:
                self.current += 1
                return line.strip().split(self.delim_type)

    def __del__(self):
        """Closes and deletes file self.f"""
        self.f.close()
        del self.f


class Manipulator:
    """Class to do manipulation on lines fed in from a generator.  Includes wide to long and calculating
    BEH statistics, and more.  Specifically designed to work with class Reader
    """
    def __init__(self, generator, SIC=False):
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
            line1 = line1 + ['Common_SIC', 'BEH_LargestPercent', 'BEH_SIC']

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

    def wide_to_long_single(self, line):
        """  Convert a single line from the wide to long format.  Time variables are inferred based on the class
        attribute self.year_indices.  Returns a nested list of the lines created from the single argument "line".
        -----------
        Keyword Arguments:
        line: The line of wide data to be transformed into the long format.

        """
        if self.SIC:  # Calculate and add the BEH attributes if this is a SIC file
            line = line + self.BEH(line)
        try:
            key, time, nontime = line[0], [line[i] for i in self.year_indices], [
                [line[i] for i in self.nonyear_indices]] * self.num_all_years  # separate key from the rest of the line
        except IndexError:  # caused by a line having only a key or not enough values, pad it with empty vals
            padding = ["" for i in range(len(self.line1) - len(line))]
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
            name_bool = False
            for config_name in local_config['name']:
                name_bool = config_name.lower() in name.lower()
                if name_bool:
                    break
        except KeyError:
            pass

        try:
            sic_exclusive_bool = sic in local_config['sic_exclusive']
        except KeyError:
            pass

        try:
            sic_range_bool = False
            for num_range in local_config['sic_range']:
                if num_range[0] <= sic <= num_range[1]:
                    sic_range_bool = True
        except KeyError:
            pass

        try:
            sic_range_2_bool = False
            for num_range in local_config['sic_range_2']:
                if num_range[0] <= sic <= num_range[1]:
                    sic_range_2_bool = True
        except KeyError:
            pass

        try:
            if local_config['emp'][0] == 'g':
                emp_bool = emp > int(local_config['emp'][1:])
            else:
                emp_bool = emp < int(local_config['emp'][1:])
        except KeyError:
            pass

        try:
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
            rankdict = dict()
            for key in true_keys:
                rankdict[key] = self.all_config[key]['ranking']


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
    def __init__(self, filepath, delim_type, generator):
        """Set object attributes and open the file for writing"""
        self.filepath = filepath
        self.delim_type = delim_type
        self.generator = generator

        self.f = open(self.filepath, 'w')

    def write_line(self, data_list):
        """Write a single line to the file self.f
        -------
        Keyword Arguments:
        data_list: list of data to be converted to str and written
        """
        self.f.write(self.delim_type.join(data_list) + '%s \n' % self.delim_type)

    def write_all(self ):
        """Perform self.write on all lines in self.generator"""
        for line in self.generator:
            self.write_line(line)

    def __del__(self):
        """Close and delete the file self.f"""
        self.f.close()
        del(self.f)

if __name__ == '__main__':
    # config_dir = 'C:\Users\jc4673\Documents\Columbia\Python_r01_Wrangle\classify_configs'
    # config_path = config_dir + r'\fast_food.txt'
    json_config = 'C:\Users\jc4673\Documents\Columbia\Python_r01_Wrangle\json_config.json'
    sic = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"
    emp = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Emp.txt"
    sales = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Sales.txt"
    company = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"

    # Create Readers
    read_sic = Reader(sic, '\t', line_limit=10)
    read_emp = Reader(emp, '\t', line_limit=10)
    read_sales = Reader(sales, '\t', line_limit=10)
    read_company = Reader(company, '\t', line_limit=10)


    classy = Classifier(json_config)
    print(classy.classify('arbys', 58120000, 5, 3))






    """
    t0 = time.time()
    filepath = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"
    read = Reader(filepath, '\t', line_limit=10**3)
    manip = Manipulator(read.line_gen, SIC=True)
    nextline = next(manip.generator)
    a = manip.wide_to_long_all()
    write = Writer('out.txt', '\t', a)
    write.writeline(manip.line1)
    write.write_all()
    t1 = time.time()
    print t1-t0
    """

