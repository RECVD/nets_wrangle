import os
import pandas as pd
import numpy as np
import Tkinter as tk
import tkFileDialog as filedialog
import itertools as it
import functions
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

    def is_class(self, config_key, name, sic, emp, sales, tradename):
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

        #convert SIC to int
        try:
            sic = int(sic)
        except ValueError:
            sic = None

        # Assess all boolean values, pass if no values are available
        try:
            name_bool = False
            for config_name in local_config['name']:
                name_bool = config_name.lower() in name.lower() or config_name.lower() in tradename.lower()
                if name_bool:
                    break
        except KeyError:
            pass

        try:
            sic_exclusive_bool = False
            sic_exclusive_bool = int(sic) in local_config['sic_exclusive']
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
                emp_bool = emp >= int(local_config['emp'][1:])
            elif local_config['emp'][0] == 'l':
                emp_bool = emp < int(local_config['emp'][1:]) and emp > 0
            else:
                emp_range = range(*[int(x) for x in local_config['emp'].split(',')])
                emp_bool = emp in emp_range
        except KeyError:
            pass

        try:
            sales_bool = False
            if local_config['sales'][0] == 'g':
                sales_bool = sales >= int(local_config['sales'][1:])
            elif local_config['sales'][0] == 'l':
                sales_bool = sales < int(local_config['sales'][1:]) and sales > 0
            else:
                sales_range = range([int(x) for x in range(local_config['sales'].split(','))])
                sales_bool = sales in sales_range
        except KeyError:
            pass

        if np.isnan(sales):
            sales_present = False
        else:
            sales_present = True

        # Assess truth cateogry based on booleans and conditional codes from config file
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
            if sic_exclusive_bool or sic_range_bool:
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
        elif condit_code == 10:
            if sic_range_bool and emp_bool and (sales_bool or not sales_present):
                return True
            else:
                return False

    def classify(self, row, BEH=False):
        """  Classify a business into a category defined in self.all_config.  If no category matches, return 'not'.
        --------------
        Keyword Arguments:
        name: name of the business to be classified
        sic: SIC code of the business to be classified
        emp: Number of employees of the business to be classified
        sales:  Yearly sales yield of the business to be classified
        """
        name = row['Company']
        if BEH == False:
            sic = row['SIC']
        else:
            sic = row['BEH_SIC']
        emp = row['Emp']
        sales = row['Sales']
        tradename = row['TradeName']

        true_keys = []
        for key, _ in self.all_config.iteritems():
            if self.is_class(key, name, sic, emp, sales, tradename):
                true_keys.append(str(key))
            else:
                continue

        if not true_keys:
            return 'not'
        else:
            return ' | '.join(true_keys)


def column_replace(column_list, term1, term2):
    """Look for term1 in any elements of column_list and replace with term2 when found"""
    return [item.replace(term1,term2) if term1 in item else item for item in column_list]

def BEH_largestpercent(group):
    #find most used SIC
    return (max(group['YearsActive'])/sum(group['YearsActive']))*100

def most_common(group):
    return group.sort_values('YearsActive').iloc[-1].SIC.astype(int)

if __name__ == "__main__":
    #define all filenames of interest
    read_dir = filedialog.askdirectory(title='Select Folder to Read Data From')
    sic_filename = read_dir + '\NETS2014_SIC.txt'
    sales_filename = read_dir + '\NETS2014_Sales.txt'
    emp_filename = read_dir + '\NETS2014_Emp.txt'
    misc_filename = read_dir + '\NETS2014_Misc.txt'
    company_filename = read_dir + '\NETS2014_Company.txt'
    writepath = filedialog.askdirectory(title='Select Folder to Write To') + '/NETS2014_Classifications_test.txt'

    cwd = os.getcwd()
    dtypes_filename = cwd + "/config/dtypes.json"
    config_filename = cwd + "/config/json_config.json"

    # Load JSON configs
    with open (dtypes_filename) as f:
        dtypes = json.load(f)

    #dtypes for more efficient reading
    sic_cols = ['DunsNumber', 'SIC8', 'SIC90', 'SIC91','SIC92','SIC93','SIC94','SIC95','SIC96','SIC97','SIC98','SIC99','SIC00',
                'SIC01','SIC02','SIC03','SIC04','SIC05','SIC06','SIC07','SIC08','SIC09','SIC10','SIC11','SIC12','SIC13',
                'SIC14', 'Industry', 'IndustryGroup']
    emp_cols = ['DunsNumber', 'Emp90','Emp91', 'Emp92','Emp93','Emp94','Emp95','Emp96','Emp97','Emp98','Emp99','Emp00',
                'Emp01','Emp02','Emp03','Emp04','Emp05','Emp06','Emp07','Emp08','Emp09','Emp10','Emp11','Emp12','Emp13',
                'Emp14']
    sales_cols = ['DunsNumber', 'Sales90','Sales91','Sales92','Sales93','Sales94','Sales95','Sales96','Sales97','Sales98',
                  'Sales99','Sales00','Sales01','Sales02','Sales03','Sales04','Sales05','Sales06','Sales07','Sales08',
                  'Sales09','Sales10','Sales11','Sales12','Sales13','Sales14']

    # create dataframe iterators
    sic_df = pd.read_table(sic_filename, dtype=dtypes['SIC'], usecols=sic_cols, index_col=['DunsNumber'], quoting=3,
                           chunksize=10**3)
    misc_df = pd.read_table(misc_filename, dtype=dtypes['Misc'], usecols=['DunsNumber', 'FirstYear', 'LastYear'], quoting=3,
                            chunksize=10**3)
    sales_df = pd.read_table(sales_filename, dtype=dtypes['Sales'], usecols=sales_cols, quoting=3, chunksize=10**3)
    emp_df = pd.read_table(emp_filename, dtype=dtypes['Emp'], usecols=emp_cols, quoting=3, chunksize=10**3)
    company_series = pd.read_table(company_filename, dtype=dtypes['Company'], usecols=['DunsNumber', 'Company', 'TradeName'],
                                   index_col=['DunsNumber'], quoting=3, chunksize=10**3)

    first = True  # Determines whether we write to a new file or append
    for sic_chunk, company_chunk, sales_chunk, emp_chunk, misc_chunk in it.izip(sic_df, company_series, sales_df, emp_df,
                                                                                misc_df): # Iterate over all dfs
        sic_chunk[['Company', 'TradeName']] = company_chunk #add company name to SIC
        sic_chunk.reset_index(inplace=True, drop=False) #remove index for joining
        # remove prefix, to not confuse the long to wide algorithm
        sic_chunk.rename(columns={'SIC8': 'Here'}, inplace=True)
        sic_chunk.columns = functions.make_fullyear(list(sic_chunk.columns), 'SIC')  #Fix years on sic

        #normalize SIC file
        nowlong = functions.l2w_pre(sic_chunk, 'SIC')
        normal = functions.normalize_df(nowlong, 'SIC', misc_chunk)

        #formatting emp
        emp_chunk.columns = functions.make_fullyear(list(emp_chunk.columns), 'Emp')
        nowlong_emp = functions.l2w_pre(emp_chunk, 'Emp')
        nowlong_emp.index.rename(['DunsNumber', 'FirstYear'], inplace=True)

        #formatting sales
        sales_chunk.columns = functions.make_fullyear(list(sales_chunk.columns), 'Sales')
        nowlong_sales = functions.l2w_pre(sales_chunk, 'Sales')
        nowlong_sales.index.rename(['DunsNumber', 'FirstYear'], inplace=True)

        #join sales, emp and sic
        final = normal.join(nowlong_sales['Sales'], how='left').join(nowlong_emp['Emp'], how='left')

        # Calculate total active years
        final['YearsActive'] = (final['LastYear'] - final.index.get_level_values(level=1))+1

        # Filter out businesses that can have different BEH_SIC than SIC (multi-sic).  Calculate BEH_largestpercent and
        # find the most common SIC code.
        grouped = final[['SIC', 'YearsActive']].groupby(level=0).filter(lambda x: len(x) > 1).groupby(level=0)
        BEH = grouped.apply(BEH_largestpercent).to_frame()
        BEH['most_common'] = grouped.apply(most_common)
        BEH = BEH.rename(columns={0 : 'BEH_LargestPercent'})

        # Create a mask for all BEH < 75 values, and assign TrueFalse to True for them
        BEH['TrueFalse'] = False
        criteria = BEH['BEH_LargestPercent'] < 75
        BEH.loc[criteria, 'TrueFalse'] = True

        # Formatting
        new = final.loc[BEH.index.get_level_values(level=0).tolist()]
        BEH = BEH.reindex(pd.MultiIndex.from_tuples(new.index), level=0)
        BEH.index.rename(('DunsNumber','FirstYear'), inplace=True)

        # Add new columns to final with default values
        final['BEH_LargestPercent'] = 100.0
        final['most_common'] = final['SIC'].astype(int)
        final['BEH_SIC'] = final['SIC'].astype(int)
        final['TrueFalse'] = False

        #Set final values in BEH to BEH values
        final.loc[BEH.index, ('BEH_LargestPercent', 'most_common', 'TrueFalse')] = BEH
        #Assign final values where BEH < 75 to most recent SIC
        final.loc[final['TrueFalse'] == True, 'BEH_SIC'] = final.loc[final['TrueFalse'] == True, 'Here']
        final.loc[final['TrueFalse'] == False, 'BEH_SIC'] = final.loc[final['TrueFalse'] == False, 'most_common']
        final.drop(['most_common', 'TrueFalse', 'Here'], axis=1, inplace=True)

        #apply classifications to each row as a new column
        classy = Classifier(config_filename)
        final['Class_List'] = final.apply(classy.classify, axis=1)
        final['BEH_Class'] = final['Class_List'][0] # set default BEH_Class value to start with before reassignment

        #Apply classifications to BEH_SIC in BEH dataframe and assign those values into final['BEH_Class']
        BEH[['Company', 'TradeName', 'Emp', 'Sales', 'BEH_SIC']] = final.loc[BEH.index, ('Company', 'TradeName', 'Emp', 'Sales', 'BEH_SIC')]
        BEH['BEH_Class'] = BEH.apply(classy.classify, axis=1, BEH=True)
        final.loc[BEH.index, 'BEH_Class'] = BEH['BEH_Class']

        # write to new txt if first, append to current if not first
        if first:
            final.to_csv(writepath, sep='\t')
            first = False
            print('.')
        else:
            final.to_csv(writepath, sep='\t', mode='a', header=False)
            print('.')

