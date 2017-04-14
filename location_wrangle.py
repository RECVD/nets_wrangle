import pandas as pd
import itertools as it
import Tkinter as tk
import tkFileDialog as filedialog

first = True #boolean for first iteration, sets whether writing to new fileor appending
# filenames for all df to be used - later to be replaced by GUI selection

company_filename = "E:\NETSDatabase2014\NETS2014_Company.txt"
address_first_filename = "E:\NETSDatabase2014\NETS2014_AddressFirst.txt"
misc_filename = "E:\NETSDatabase2014\NETS2014_Misc.txt"
move_filename = "E:\NETSDatabase2014\NETS2014_Move.txt"
writepath = r"E:\NETSDatabase2014_wrangled\NETS2014_Location_primsec.txt"

"""
company_filename = filedialog.askopenfilename(title='Select ASCI Company File')
address_first_filename = filedialog.askopenfilename(title='Select ASCI Address First File')
move_filename = filedialog.askopenfilename(title='Select ASCI Move File')
misc_filename = filedialog.askopenfilename(title='Select ASCI Misc File')
writepath = filedialog.askdirectory(title='Select File to Write To') + '/NETS2014_Location_primsec.txt'
"""
#read all data frame as generators, chunksize may need to be decreased for low-memory machines
company_df = pd.read_table(company_filename, index_col=['DunsNumber'],
                           usecols=['DunsNumber','Company', 'Address', 'City', 'State', 'ZipCode'],
                           chunksize=10**6)
address_first_df = pd.read_table(address_first_filename, index_col=['DunsNumber'],
                                 usecols=['DunsNumber', 'Address_First', 'City_First', 'CityCode_First',
                                          'State_First', 'ZipCode_First', 'FipsCounty_First'],
                                 chunksize=10**6)
misc_df = pd.read_table(misc_filename, index_col=['DunsNumber'],
                        usecols=['DunsNumber','FirstYear', 'LastYear', 'Latitude', 'Longitude', 'LevelCode',
                                 'CityCode', 'FipsCounty'], chunksize=10**6)

#smaller table with mismatched indices so the whole thing gets loaded into memory
move_df = pd.read_table(move_filename, index_col=['DunsNumber', 'MoveYear'],
                        usecols=['DunsNumber', 'MoveYear', 
                                 'OriginAddress', 'OriginCity', 'OriginState', 'OriginZIP', 'OriginFIPSCounty',
                                 'DestAddress', 'DestCity', 'DestState', 'DestZIP', 'DestFIPSCounty',
                                 'OriginLatitude', 'OriginLongitude', 'OriginLevelCode'])

for company_chunk, add_first_chunk, misc_chunk in it.izip(company_df, address_first_df, misc_df):
    # index is initially in reverse chronological order
    move_df.sort_index(inplace=True)

    # Join company with necessary piecees from misc
    company_chunk = company_chunk.join(misc_chunk[['LastYear', 'Latitude', 'Longitude', 'LevelCode', 'FipsCounty']])
    company_chunk.rename(columns={'Address': 'PrimAdd', #rename columns to fit prim/sec scheme
                                  'LastYear': 'FirstYear',
                                  'City': 'PrimCity',
                                  'State': 'PrimState',
                                  'ZipCode': 'PrimZip',
                                  'FipsCounty': 'PrimFipsCounty'}, inplace=True)
    company_chunk.set_index('FirstYear', append=True, inplace=True) #Use FirstYear to create MultiIndex for joining

    # Join address first with FirstYear and form Multiindex
    add_first_chunk = add_first_chunk.join(misc_chunk['FirstYear'])
    add_first_chunk = add_first_chunk.set_index('FirstYear', append=True)
    add_first_chunk.rename(columns={'Address_First':'SecAdd', #rename columns to fit prim/sec scheme
                                    'City_First': 'SecCity',
                                    'State_First': 'SecState',
                                    'ZipCode_First': 'SecZip',
                                    'FipsCounty_First' :'SecFipsCounty'}, inplace=True)

    #get move_chunk based on the last item in company_chunk
    company_first = company_chunk.index.get_level_values('DunsNumber')[0]
    company_last = company_chunk.index.get_level_values('DunsNumber')[-1]
    move_chunk = move_df.loc[company_first:company_last, :]
    move_chunk.index.names = ['DunsNumber', 'FirstYear']

    #rename move_chunk columns to fit prim/sec scheme
    move_chunk.rename(columns={'OriginAddress':'PrimAdd', 'DestAddress':'SecAdd',
                               'OriginCity': 'PrimCity', 'DestCity': 'SecCity',
                               'OriginState': 'PrimState', 'DestState': 'SecState',
                               'OriginZIP': 'PrimZip', 'DestZIP': 'SecZip',
                               'OriginLatitude': 'Latitude', 'OriginLongitude': 'Longitude', 'OriginLevelCode': 'LevelCode',
                               'OriginFIPSCounty': 'PrimFipsCounty', 'DestFIPSCounty': 'SecFipsCounty'}, inplace=True)

    #Create the secondary address df with pieces of both move and add-first
    sec_add = pd.concat([move_chunk[['SecAdd', 'SecCity', 'SecState', 'SecZip', 'SecFipsCounty']], add_first_chunk]).sort_index()
    #Primary address df with pieces of move and company
    primadd = pd.concat([move_chunk[['PrimAdd', 'PrimCity', 'PrimState', 'PrimZip', 'PrimFipsCounty', 'Latitude', 'Longitude',
                                     'LevelCode']], company_chunk]).sort_index()

    #drop primary_address index and set it as a copy of sec_add index, then join
    prim_add = primadd.reset_index(drop=False)
    prim_add.index = sec_add.index.copy()
    joined = prim_add.join(sec_add, how='outer')
    joined['Company'].bfill(inplace=True) #fill in missing doubles of company names

    #leftover formatting
    del joined['DunsNumber'] #leftover extra
    joined.rename(columns={'FirstYear':'LastYear'}, inplace=True)

    #create and add BEH_LOC and BEH_ID
    joined['BEH_LOC'] = joined.groupby(level=0).cumcount() + 1
    joined['BEH_ID'] = joined['BEH_LOC'] * (10 ** 9) + 10 ** 10 + joined.index.get_level_values(level=0)

    # reorder columns for readability
    column_order = ['LastYear', 'BEH_LOC', 'BEH_ID', 'Company', 'PrimAdd', 'PrimCity', 'PrimFipsCounty', 'PrimState',
                    'PrimZip', 'SecAdd', 'SecCity', 'SecFipsCounty', 'SecState', 'SecZip', 'Latitude', 'Longitude',
                    'LevelCode']
    joined = joined[column_order]

    #write to new txt if first, append to current if not first
    if first:
        joined.to_csv(writepath, sep='\t')
        print('.')
        first = False
    else:
        joined.to_csv(writepath, sep='\t', mode='a', header=False)
        print('.')

