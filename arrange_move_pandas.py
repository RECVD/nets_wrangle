import numpy as np
import pandas as pd


def combine_chunks(company_chunk, misc_chunk, add_first_chunk):
    company_chunk = company_chunk.join(misc_chunk, how='outer')
    company_chunk = company_chunk.join(add_first_chunk)
    company_chunk.index.names = ['DunsNumber','MoveYear']

    company_last = company_chunk.index[-1][0]

    move_chunk = move_df.loc[:company_last,:]
    final_joined = company_chunk.join(move_chunk, how='outer')
    return final_joined

def group_chunks(chunk):
    joined_grouped = chunk.groupby(level='DunsNumber')
    return joined_grouped

def organize_lastyear(joined_grouped):
    new_lastyear = [0] * len(joined_grouped)
    for i, (_, group) in enumerate(joined_grouped):
        if len(group) > 1:
            single_lastyear = group.loc[:,'LastYear'].iloc[0]
            lastyear_list = group.index.get_level_values('MoveYear')
            lastyear_list = [item-1 for item in lastyear_list]
            lastyear_list.append(single_lastyear)
            del lastyear_list[0]
            new_lastyear[i] = lastyear_list
            #group.loc[:,'LastYear'] = np.array(lastyear_list)
        else:
            new_lastyear[i] = [group.loc[:,'LastYear'].iloc[0]]
            #new_lastyear.append(group.loc[:,'LastYear'].iloc[0])
    new_lastyear = [item for sublist in new_lastyear for item in sublist]
    return new_lastyear

def organize_address(joined_grouped):
    prim_adds = []
    sec_adds = []
    for (_, group) in joined_grouped:
        if len(group) == 1:
            prim_adds.append(group['Address'][0])
            sec_adds.append(group['Address_First'][0])
        else:
            groupiter = group.iterrows()
            row1 = next(groupiter)[1]
            first_sec = row1['Address_First']
            last_prim = row1['Address']
            sec_adds.append(first_sec)
            for _,row in groupiter:
                prim_adds.append(row['OriginAddress'])
                sec_adds.append(row['DestAddress'])
            prim_adds.append(last_prim)
    return prim_adds, sec_adds

def drop(final_joined):
    return final_joined.drop(['LastYear', 'Address', 'Address_First', 'OriginAddress', 'DestAddress'], axis=1)

def last_join(final_joined, new_lastyear, prim_adds, sec_adds):
    final_joined['LastYear'] = pd.Series(np.array(new_lastyear), index=final_joined.index)
    final_joined['PrimAddress'] = pd.Series(np.array(prim_adds), index=final_joined.index)
    final_joined['SecAddress'] = pd.Series(np.array(sec_adds), index=final_joined.index)
    return final_joined

if __name__ == "__main__":
    # filenames for all df to be used
    company_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"
    address_first_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_AddressFirst.txt"
    misc_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Misc.txt"
    move_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\Move_sorted.txt"

    company_df = pd.read_table(company_filename, index_col=['DunsNumber'],
                               usecols=['DunsNumber','Company', 'Address'],
                               dtype={'DunsNumber': np.int32, 'Company': 'str', 'Address': 'str'},
                               chunksize=10**5)
    add_first_df = pd.read_table(address_first_filename, index_col=['DunsNumber'],
                                 usecols=['DunsNumber', 'Address_First'],
                                 dtype={'DunsNumber': np.int32, 'Company': 'str', 'Address': 'str'},
                                 chunksize=10**5)
    misc_df = pd.read_table(misc_filename, index_col=['DunsNumber', 'FirstYear'],
                            usecols=['DunsNumber', 'FirstYear', 'LastYear'],
                            dtype={'DunsNumber': np.int32, 'FirstYear': np.int32, 'LastYear': np.int32},
                            chunksize=10**5)

    move_df = pd.read_table(move_filename, index_col=['DunsNumber', 'MoveYear'],
                            usecols=['DunsNumber', 'MoveYear', 'OriginAddress', 'DestAddress'],
                            dtype={'DunsNumber': np.int32, 'MoveYear': np.int32, 'OriginAddress': 'str',
                                   'DestAddress': 'str'})

    company_chunk = company_df.get_chunk()
    add_first_chunk = add_first_df.get_chunk()
    misc_chunk = misc_df.get_chunk()

    combined = combine_chunks(company_chunk, misc_chunk, add_first_chunk)
    combined_grouped = group_chunks(combined)

    new_lastyear = organize_lastyear(combined_grouped)
    primadds, secadds = organize_address(combined_grouped)
    combined = drop(combined)
    final_joined = last_join(combined, new_lastyear, primadds, secadds)

