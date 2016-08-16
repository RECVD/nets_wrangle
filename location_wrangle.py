import pandas as pd
import numpy as np
from time import time


# filenames for all df to be used
company_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Company.txt"
address_first_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_AddressFirst.txt"
misc_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Misc.txt"
move_filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\Move_sorted.txt"

company_df = pd.read_table(company_filename, index_col=['DunsNumber'],
                           usecols=['DunsNumber','Company', 'Address', 'City', 'State', 'ZipCode'],
                           chunksize=10**3)
address_first_df = pd.read_table(address_first_filename, index_col=['DunsNumber'],
                                 usecols=['DunsNumber', 'Address_First', 'City_First', 'CityCode_First',
                                          'State_First', 'ZipCode_First', 'FipsCounty_First'],
                                 chunksize=10**3)
misc_df = pd.read_table(misc_filename, index_col=['DunsNumber'],
                        usecols=['DunsNumber','FirstYear', 'LastYear', 'Latitude', 'Longitude', 'LevelCode',
                                 'CityCode', 'FipsCounty'], chunksize=10**3)

move_df = pd.read_table(move_filename, index_col=['DunsNumber', 'MoveYear'],
                        usecols=['DunsNumber', 'MoveYear', 
                                 'OriginAddress', 'OriginCity', 'OriginState', 'OriginZIP', 'OriginFIPSCounty',
                                 'DestAddress', 'DestCity', 'DestState', 'DestZIP', 'DestFIPSCounty',
                                 'OriginLatitude', 'OriginLongitude', 'OriginLevelCode'])


t0=time()

company_chunk = company_df.get_chunk()
add_first_chunk = address_first_df.get_chunk()
misc_chunk = misc_df.get_chunk()




company_chunk = company_chunk.join(misc_chunk[['LastYear', 'Latitude', 'Longitude', 'LevelCode', 'FipsCounty']])
company_chunk
company_chunk.rename(columns={'Address': 'PrimAdd', 
                              'LastYear': 'FirstYear',
                              'City': 'PrimCity',
                              'State': 'PrimState',
                              'ZipCode': 'PrimZip',
                              'FipsCounty': 'PrimFipsCounty'}, inplace=True)




add_first_chunk = add_first_chunk.join(misc_chunk['FirstYear'])
add_first_chunk = add_first_chunk.set_index('FirstYear', append=True)
add_first_chunk.rename(columns={'Address_First':'SecAdd',
                                'City_First': 'SecCity',
                                'State_First': 'SecState',
                                'ZipCode_First': 'SecZip',
                                'FipsCounty_First' :'SecFipsCounty'}, inplace=True)



company_last = company_chunk.index[-1]
move_chunk = move_df.loc[:company_last,:]
move_chunk.index.names = ['DunsNumber', 'FirstYear']
move_chunk.rename(columns={'OriginAddress':'PrimAdd', 'DestAddress':'SecAdd',
                           'OriginCity': 'PrimCity', 'DestCity': 'SecCity',
                           'OriginState': 'PrimState', 'DestState': 'SecState',
                           'OriginZIP': 'PrimZip', 'DestZIP': 'SecZip',
                           'OriginLatitude': 'Latitude', 'OriginLongitude': 'Longitude', 'OriginLevelCode': 'LevelCode',
                           'OriginFIPSCounty': 'PrimFipsCounty', 'DestFIPSCounty': 'SecFipsCounty'}, inplace=True)



sec_add = pd.concat([move_chunk[['SecAdd', 'SecCity', 'SecState', 'SecZip', 'SecFipsCounty']], add_first_chunk]).sort_index()



company_chunk.set_index('FirstYear', append=True, inplace=True)


primadd = pd.concat([move_chunk[['PrimAdd', 'PrimCity', 'PrimState', 'PrimZip', 'PrimFipsCounty', 'Latitude', 'Longitude',
                                 'LevelCode']], company_chunk]).sort_index()


prim_add = primadd.reset_index(drop=False) #was True


prim_add.index = sec_add.index.copy()



joined = prim_add.join(sec_add, how='outer')
joined['Company'].bfill(inplace=True)


del joined['DunsNumber']



joined.rename(columns={'FirstYear':'LastYear'}, inplace=True)



column_order = ['LastYear', 'Company', 'PrimAdd', 'PrimCity', 'PrimFipsCounty', 'PrimState', 'PrimZip',
                'SecAdd', 'SecCity', 'SecFipsCounty', 'SecState', 'SecZip', 'Latitude', 'Longitude', 'LevelCode']



joined = joined[column_order]

joined.to_csv('NETS2013_LocationsSample.txt', sep='\t')
print(time() - t0)
