import pandas as pd
import numpy as np
import random
import itertools as it

import functions

# Filenames
add99name = "E:\NETS2014_AddressSpecial90to99.txt"
add14name = "E:\NETS2014_AddressSpecial00to14.txt"
miscname = "E:\NETSDatabase2014\NETS2014_Misc.txt"
writepath = "E:\NETSDatabase2014_wrangled\NETS2014_Location.txt"


#have to rework this to preset column dtypes
# Create reading iterators
ad99df = pd.read_table(add99name, index_col=['DunsNumber'],  error_bad_lines=False, chunksize=10**6)
ad14df = pd.read_table(add14name, index_col=['DunsNumber'], error_bad_lines=False, chunksize=10**6)
miscdf = pd.read_table(miscname, usecols=['DunsNumber', 'FirstYear', 'LastYear'],
                       dtype={'DunsNumber': np.int32, 'FirstYear': np.int64, 'LastYear': np.int32},
                       chunksize=10**6)


first = True #used for writing purposes to determine first iteration
for ad99, ad14, misc_chunk in it.izip(ad99df, ad14df, miscdf):
    #combine dataframes across years, drop rows with no values
    ad99 = pd.concat([ad99, ad14], axis=1)
    ad99.dropna(how='all', inplace=True)
    ad99.columns = [col.lower() if 'CityCode' in col else col for col in ad99.columns] #make citycode lowercase for formatting

    # Column Name Formatting
    ad99.columns = functions.make_fullyear(ad99.columns, 'Address')
    ad99.columns = functions.make_fullyear(ad99.columns, 'City')
    ad99.columns = functions.make_fullyear(ad99.columns, 'State')
    ad99.columns = functions.make_fullyear(ad99.columns, 'ZIP')
    ad99.columns = functions.make_fullyear(ad99.columns, 'citycode')
    ad99.columns = functions.make_fullyear(ad99.columns, 'FipsCounty')
    ad99.columns = functions.make_fullyear(ad99.columns, 'CBSA')

    # Splitting into separate dfs per variable
    address = ad99[[col for col in ad99.columns if 'Address' in col]]
    address.reset_index(drop=False, inplace=True)
    address = address.astype(basestring)

    city = ad99[[col for col in ad99.columns if 'City' in col]]
    city.reset_index(drop=False, inplace=True)
    city = city.astype(basestring)

    state = ad99[[col for col in ad99.columns if 'State' in col]]
    state.reset_index(drop=False, inplace=True)
    state = state.astype(basestring)

    zipp = ad99[[col for col in ad99.columns if 'ZIP' in col]]
    zipp.reset_index(drop=False, inplace=True)
    zipp = zipp.apply(pd.to_numeric, errors='coerce', downcast='unsigned')

    citycode = ad99[[col for col in ad99.columns if 'citycode' in col]]
    citycode.reset_index(drop=False, inplace=True)
    citycode = citycode.apply(pd.to_numeric, errors='coerce', downcast='unsigned')

    fips = ad99[[col for col in ad99.columns if 'FipsCounty' in col]]
    fips.reset_index(drop=False, inplace=True)
    fips = fips.apply(pd.to_numeric, errors='coerce', downcast='unsigned')

    cbsa = ad99[[col for col in ad99.columns if 'CBSA' in col]]
    cbsa.reset_index(drop=False, inplace=True)
    cbsa = cbsa.apply(pd.to_numeric, errors='coerce', downcast='unsigned')

    # Long to wide conversions
    address_l = functions.l2w_pre(address, 'Address')
    city_l = functions.l2w_pre(city, 'City')
    state_l = functions.l2w_pre(state, 'State')
    zipp_l = functions.l2w_pre(zipp, 'ZIP')
    citycode_l = functions.l2w_pre(citycode, 'citycode')
    fips_l = functions.l2w_pre(fips, 'FipsCounty')
    cbsa_l = functions.l2w_pre(cbsa, 'CBSA')

    #Join, normalize, strip strings, replace empty str with NaN and drop duplicated lines
    addcity = address_l.join(city_l).join(state_l).join(zipp_l).join(citycode_l).join(fips_l).join(cbsa_l)
    normal = functions.normalize_df(addcity, 'Address', misc_chunk)
    normal['BEH_LOC'] = normal.groupby(level=0).cumcount() + 1
    normal['BEH_ID'] = normal['BEH_LOC'] * (10 ** 9) + 10 ** 10 + normal.index.get_level_values(level=0)
    normal['Address'] = normal['Address'].map(lambda x: x.strip())
    normal.replace("", np.nan, inplace=True)
    #normal.drop_duplicates(['Address', 'State'], inplace=True)

    if first:
        normal.to_csv(writepath, sep='\t', float_format='%.f')
        first = False
        print('.')

    else:
        normal.to_csv(writepath, sep='\t', mode='a', header=False, float_format='%.f')
        print('.')
