import pandas as pd

# Function Definitions


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


def l2w_pre(df, varname):
    """
    Changes main dataframe from wide to long.  Requires pre-processed full years
    
    df:  DataFrame to be transformed from wide to long
    varname:  Column name of the transformed variable
    """
    
    long_df = pd.wide_to_long(df, [varname], i='DunsNumber', j='year')
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

