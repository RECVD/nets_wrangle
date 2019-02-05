    import numpy as np
import pandas as pd
import random

# Function Definitions


def make_fullyear(partyear_list, prefix):
    """Function to redefine 'partial year', i.e '99' into 'full year', i.e '1999'.
    -------------------
    Keyword Arguments:
    partyear_list:  List of column headers, some of which will include partial years
    prefix:  Prefix that identifies that there will be a partial year following

    If prefix is a list, we assume that all elements in the list have a prefix and it is completely
    re-formed
    """
    if type(prefix) == str:
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

    else:
        prefix_len = [len(thing) for thing in prefix]
        prefix_dict = dict(zip(prefix, prefix_len))
        fullyear_list = []
        for title in partyear_list:
            partyear = title[-2:]
            if partyear[0] == '0' or partyear[0] == '1':
                fullyear = title[:-2] + '20' + partyear
            else:
                fullyear = title[:-2] + '19' + partyear

            fullyear_list.append(fullyear)
            """
            #figure out if we'll add '19' or '20', do so and append to the new list
            partyear = title[prefix_dict[pre]:]
            if partyear[0] == '0' or partyear[0] == '1':
                partyear = pre + '20'+ partyear
            else:
                partyear = pre + '19' + partyear
            fullyear_list.append(partyear)
            """

    return fullyear_list


def l2w_pre(df, varname):
    """
    Changes main dataframe from wide to long.  Requires pre-processed full years
    
    df:  DataFrame to be transformed from wide to long
    varname:  Column name of the transformed variable
    """
    
    long_df = pd.wide_to_long(df, [varname], i='DunsNumber', j='Year')
    long_df.sort_index(inplace=True)
    long_df.dropna(inplace=True)
    
    return long_df


def normalize_df(df, varname, misc):
    """
    Changes database from long form to normalized form, only including updates and removing redundant data
    
    df: DataFrame in the long format.  Should have MultiIndex (DunsNumber, Year)
    misc:  misc dataframe containing 'FirstYear' and 'LastYear' variables, should have no set index
    varname:  Column name of the tranformed variable
    """
    unique = df[varname].groupby(level=0).unique() #remove duplicates for each DunsNumber
               
    #Create column to denote whether the variable changed at all for each Duns 
    change = unique.apply(lambda x: len(x) > 1).to_frame()
    change.columns = ['Change']
    df = change.join(df)
    
    #Drop duplicates, add DunsNumber as column to ensure no deletion between different businesses with identical rows
    df['DunsNumber'] = df.index.get_level_values(level=0)
    df = df.drop_duplicates()
    del df['DunsNumber']
    df.index.names = ['DunsNumber', 'FirstYear'] #formatting
    
    misc['FirstYear'] = misc['FirstYear'] + 1 #adjust FirstYear as needed and set as index
    misc.set_index(['DunsNumber', 'FirstYear'], inplace=True)
    
    #Join FirstYear and LastYear in from misc, and fill values forward
    joined = misc.join(df, how='outer').ffill()
    multi = joined[joined['Change'] == True] #df with only businesses that had changes
    
    #Diagonal shift to fix years for multi businesses
    shift_year = lambda joined: joined.index.get_level_values('FirstYear').to_series().shift(-1)
    lastyear = multi.groupby(level=0).apply(shift_year).combine_first(multi.LastYear).astype(int).rename('Lastyear')
    multi['LastYear'] = lastyear
    
    #Join multi fixes into the original df and remove the Change column
    joined.loc[multi.index] = multi
    del joined['Change']
    
    return joined


def normalize_nomisc(df, var1, var2=None):
    """"
    Changes database from long form to normalized form, only including updates and removing redundant data

    df: DataFrame in the long format.  Should have MultiIndex (DunsNumber, Year)
    var1:  Column name of the initial transformed variable
    var2: Column name of the optional second transformed variable
    """

    #Generate df of FirstYear and LastYear
    df.reset_index(inplace=True, drop=False)
    grouped = df[['DunsNumber', 'Year']].groupby('DunsNumber')
    firstyear = grouped.first().rename(columns={'Year': 'FirstYear'})
    lastyear = grouped.last().rename(columns={'Year': 'LastYear'})
    misc = pd.concat([firstyear, lastyear], axis=1)
    misc.set_index('FirstYear', append=True, inplace=True)
    df.set_index(['DunsNumber', 'Year'], inplace=True)

    unique_var1 = df[var1].groupby(level=0).unique() #remove duplicates for each DunsNumber

    if var2: #if we have 2 variables
        unique_var2 = df[var2].groupby(level=0).unique()
        change2 = unique_var2.apply(lambda x: len(x) > 1).to_frame()

    #Create column to denote whether the variable changed at all for each Duns
    change1 = unique_var1.apply(lambda x: len(x) > 1).to_frame()

    if var2: # Merge changes together (one or the other) if using two variables
        change = (change1[var1] | change2[var2]).to_frame()
    else:
        change = change1

    change.columns = ['Change']
    df = change.join(df)

    #Drop duplicates, add DunsNumber as column to ensure no deletion between different businesses with identical rows
    df['DunsNumber'] = df.index.get_level_values(level=0)
    df = df.drop_duplicates()
    del df['DunsNumber']
    df.index.names = ['DunsNumber', 'FirstYear'] #formatting

    #Join FirstYear and LastYear in from misc, and fill values forward
    joined = misc.join(df, how='outer')
    joined['LastYear'] = joined['LastYear'].groupby(level=0).ffill()
    multi = joined[joined['Change'] == True] #df with only businesses that had changes

    #Diagonal shift to fix years for multi businesses
    shift_year = lambda joined: joined.index.get_level_values('FirstYear').to_series().shift(-1) - 1
    lastyear = multi.groupby(level=0).apply(shift_year).combine_first(multi['LastYear']).rename('Lastyear')
    multi['LastYear'] = lastyear

    #Join multi fixes into the original df and remove the Change column
    joined.loc[multi.index] = multi
    joined['LastYear'] = joined['LastYear'].astype('int64')
    del joined['Change']

    return joined

def random_sample(df, num_values):
    duns_sample = random.sample(df['DunsNumber'].unique().tolist(), num_values)
    df_sample = df[df['DunsNumber'].isin(duns_sample)].set_index(['DunsNumber', 'FirstYear'])

    return df_sample

def normal2long(df):
    """
    Transforms a data frame from the normal format to the long one

    parameters:  df:  a data frame with a numerical index
    """
    # Create a list containing every individual year for this chunk

    df['YearsActive'] = df['LastYear'] - df['FirstYear'] + 1
    firstyear = df['FirstYear'].tolist()
    lastyear = df['LastYear'].tolist()
    year_nested = [range(x, y+1) for x,y in zip(firstyear, lastyear)]
    year = pd.Series([item for sublist in year_nested for item in sublist])

    # Make multiple entries for each business active for >1 year
    class_chunk2 = df.loc[np.repeat(df.index.values, df['YearsActive'])].reset_index(drop=True)

    class_chunk2['Year'] = year
    class_chunk2['Year'] = class_chunk2['Year']#.astype(int)

    # Drop unessecary columns and set a MultiIndex
    class_chunk2.drop(labels=['FirstYear', 'LastYear'], axis=1, inplace=True)
    class_chunk2.set_index(['DunsNumber', 'Year'], drop=True, inplace=True)

    # Clear duplicated years for businesses who changed SIC codes
    class_chunk2 = class_chunk2[~class_chunk2.index.duplicated(keep='last')]
    del class_chunk2['YearsActive']

    return class_chunk2
