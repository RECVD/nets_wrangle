import pandas as pd
import itertools as it
import json

class Classifier:
    """
    Class used in the classification of businesses based on SIC code, number of employees, annual sales,
    and company name based on the schema outlined in json_config
    """
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

    def classify(self, row):
        """  Classify a business into a category defined in self.all_config.  If no category matches, return 'not'.
        --------------
        Keyword Arguments:
        name: name of the business to be classified
        sic: SIC code of the business to be classified
        emp: Number of employees of the business to be classified
        sales:  Yearly sales yield of the business to be classified
        """
        name = row['Company']
        sic = row['SIC']
        emp = row['Emp']
        sales = row['Sales']

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


def make_fullyear(partyear_list, prefix):
    """Function to redefine 'partial year', i.e '99' into 'full year', i.e '1999'.
    -------------------
    Keyword Arguments:
    partyear_list:  List of column headers, some of which will include partial years
    prefix:  Prefix that identifies that there will be a partial year following
    """
    prefix_len = len(prefix)
    fullyear_list = []
    for title in partyear_list:
        #append as is if the prefix isn't present
        if title[:prefix_len] != prefix:
            fullyear_list.append(title)
        else:
            #figure out if we'll add '19' or '20', do so and append to the new list
            partyear = title[prefix_len:]
            if partyear[0] == '0' or partyear[0] == '1':
                partyear = prefix + '20'+ partyear
            else:
                partyear = prefix + '19' + partyear
            fullyear_list.append(partyear)
    return fullyear_list

def column_replace(column_list, term1, term2):
    """Look for term1 in any elements of column_list and replace with term2 when found"""
    return [item.replace(term1,term2) if term1 in item else item for item in column_list]

#define all filenames of interest
sic_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"
sales_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Sales.txt"
emp_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Emp.txt"
misc_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Misc.txt"
company_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"
writepath = 'C:\Users\jc4673\Documents\Columbia\NETS2013_Wrangled\NETS2013_Classifications.txt'

# create dataframe iterators
sic_df = pd.read_table(sic_filename, index_col=['DunsNumber'], chunksize=10**2)
misc_df = pd.read_table(misc_filename, usecols=['DunsNumber', 'FirstYear', 'LastYear'], chunksize=10**2)
sales_df = pd.read_table(sales_filename, chunksize=10**2)
emp_df = pd.read_table(emp_filename, chunksize=10**2)
company_series = pd.read_table(company_filename, usecols=['DunsNumber', 'Company'], index_col=['DunsNumber'], chunksize=10**2)

first = True  # Determines whether we write to a new file or append
for sic_chunk, company_chunk, sales_chunk, emp_chunk, misc_chunk in it.izip(sic_df, company_series, sales_df, emp_df,
                                                                            misc_df): # Iterate over all dfs

    sic_chunk['Company'] = company_chunk #add company name to SIC
    sic_chunk.reset_index(inplace=True) #remove index for joining
    sic_chunk.drop(['SIC2', 'SIC3', 'SIC4', 'SIC6', 'SIC8_2', 'SIC8_3', 'SIC8_4', 'SIC8_5', 'SIC8_6'],
                   axis=1, inplace=True) # We don't need these
    # remove prefix, to not confuse the long to wide algorithm
    sic_chunk.rename(columns={'SIC8': 'Here', 'SICChange':'Change'}, inplace=True)
    sic_chunk.columns = make_fullyear(list(sic_chunk.columns), 'SIC')  #Fix years on sic

    # convert to long, sort, and drop null years
    nowlong = pd.wide_to_long(sic_chunk, ['SIC'], i='DunsNumber', j='year')
    nowlong.sort_index(inplace=True)
    nowlong.dropna(how='any', inplace=True)
    nowlong.drop_duplicates(inplace=True)
    nowlong.index.names = ['DunsNumber', 'FirstYear']

    misc_chunk['FirstYear'] = misc_chunk['FirstYear'] + 1 # correct for differences in year
    misc_chunk.set_index(['DunsNumber', 'FirstYear'], inplace=True)

    joined = misc_chunk.join(nowlong, how='outer').ffill() #merge in LastYear and fill empty vals forward

    # rectify lastyear column to match actuality
    shift_year = lambda joined: joined.index.get_level_values('FirstYear').to_series().shift(-1)
    lastyear = joined.groupby(level=0).apply(shift_year) \
        .combine_first(joined.LastYear).astype(int) \
        .rename('LastYear')
    joined['LastYear'] = lastyear

    #formatting emp
    emp_chunk.columns = column_replace(list(emp_chunk.columns), 'EmpC', 'C')
    emp_chunk.rename(columns={'EmpHere': 'Here', 'EmpHereC': 'HereC'}, inplace=True)
    step1 = make_fullyear(list(emp_chunk.columns), 'Emp')
    step2 = make_fullyear(step1, 'C')
    emp_chunk.columns = step2

    # Convert emp to long  and set index
    nowlong_emp = pd.wide_to_long(emp_chunk, ['C', 'Emp'], i='DunsNumber', j='year').sort_index().dropna()
    nowlong_emp.index.names = ['DunsNumber', 'FirstYear']

    #formatting sales
    sales_chunk.columns = column_replace(list(sales_chunk.columns), 'SalesC', 'C')
    sales_chunk.rename(columns={'SalesHere': 'Here', 'SalesHereC': 'HereC', 'SalesGrowth': 'Growth',
                                'SalesGrowthPeer': 'GrowthPeer'}, inplace=True)
    step1 = make_fullyear(list(sales_chunk.columns), 'Sales')
    step2 = make_fullyear(step1, 'C')
    sales_chunk.columns = step2

    #convert sales to long and set index
    nowlong_sales = pd.wide_to_long(sales_chunk, ['C', 'Sales'], i='DunsNumber', j='year').sort_index().dropna()
    nowlong_sales.index.names = ['DunsNumber', 'FirstYear']

    #join sales, emp and sic
    final = joined.join(nowlong_sales['Sales'], how='left').join(nowlong_emp['Emp'], how='left')

    #apply classifications to each row as a new column
    classy = Classifier('C:/Users/jc4673/Documents/Columbia/nets_wrangle/json_config.json')
    final['Class'] = final.apply(classy.classify, axis=1)

    # write to new txt if first, append to current if not first
    if first:
        final.to_csv(writepath, sep='\t')
        first = False
    else:
        final.to_csv(writepath, sep='\t', mode='a', header=False)


