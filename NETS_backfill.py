import numpy as np
import pandas as pd
import Tkinter as tk
import tkFileDialog as filedialog

import functions as fx
import Normal2Long as n2l


# Read in all files
quality_file =  filedialog.askopenfilename(title= 'Please select the quality file')
location_file = filedialog.askopenfilename(title= 'Please select the location file')
crosswalk_file = filedialog.askopenfilename(title= 'Please select the crosswalk file')
writepath =  filedialog.askdirectory(title="Select Folder to write to") + '/NETS2014_Location_bfill.txt'

loc = pd.read_table(location_file, index_col=['DunsNumber', 'BEH_LOC'])
quality = pd.read_table(quality_file, dtype={'BEH_ID' : 'int64', 'Loc_name': 'object'})
crosswalk = pd.read_csv(crosswalk_file)

# Rename columns for comparison, set & sort indices for joining
crosswalk.columns = ['DunsNumber', 'BEH_LOC', 'BEH_ID']
crosswalk.set_index('BEH_ID', inplace=True)
crosswalk.sort_index(inplace=True)

quality.columns = ['BEH_ID', 'Loc_name'] 
quality.set_index('BEH_ID', inplace=True)
quality.sort_index(inplace=True)

#Join quality to crosswalk (which is to help join quality to location)
qual = quality.join(crosswalk, how='left')

# Reset Index to include DunsNumber and sort
qual.reset_index(inplace=True)
qual.set_index(['DunsNumber', 'BEH_LOC'], inplace=True)
del qual['BEH_ID']
qual.sort_index(inplace=True)

#Join qual to loc
loc_qual = qual.join(loc, how='inner')

#Add flag column to indicate backfilling
loc_qual['backfill_flag'] = 0

#Get all of them with bad DunsNumber
loc_bad = loc_qual[loc_qual['Loc_name'].isin(['Zipcode', 'PlacesAdmin'])]
loc_bad_full = loc_qual[loc_qual.index.isin(loc_bad.index.get_level_values(0).tolist(), level=0)]

#Subset to only include groups where len > 1
loc_bad_full = loc_bad_full.groupby(level=0).filter(lambda x: len(x) > 1)
loc_bad_full.reset_index(drop=False, inplace=True)

# Cleanup
del loc_bad_full['BEH_LOC']
del loc_bad_full['BEH_ID']

#Subsetted loc to long
loc_long = n2l.normal2long(loc_bad_full).sort_index()

nancopy = loc_long.copy() # Need to keep around original for joining back in
nancopy[nancopy['Loc_name'].isin(['Zipcode', 'PlacesAdmin', 'NameStreet'])] = np.nan # Unnaceptable to nan
nancopy.loc[nancopy['backfill_flag'].isnull(), ['backfill_flag']]= 1
# Backfill, and combine back to the original with backfilled having priority
loc_long_bfill = nancopy.groupby(level=0).bfill()
loc_long_bfill.loc[loc_long_bfill['ZIP'].isnull(), ['backfill_flag']]= 0
loc_long_bfill = loc_long_bfill.combine_first(loc_long)

normal = fx.normalize_nomisc(loc_long_bfill, 'Address', 'City') #Re-normalize

# Compute new BEH_LOC and BEH_ID
normal['BEH_LOC'] = normal.groupby(level=0).cumcount() + 1
normal['BEH_ID'] = normal['BEH_LOC'] * (10 ** 9) + 10 ** 10 + normal.index.get_level_values(level=0)

# Housekeeping
loc_qual.reset_index(inplace=True, drop=False)
loc_qual.set_index(['DunsNumber', 'FirstYear'], inplace=True)

# Get list of all the bad Duns, replace them in the original df with newly calculated values, and drop nans
bad_duns = list(set(loc_bad_full['DunsNumber']))
loc_qual[loc_qual.index.isin(bad_duns, level=0)] = normal
loc_qual.dropna(how='all', inplace=True)

#switch the order
col_order = ['LastYear', 'Address', 'City', 'State', 'ZIP', 'citycode', 'FipsCounty', 'CBSA', 'Loc_name', 'BEH_LOC',
             'BEH_ID', 'backfill_flag']
loc_qual = loc_qual[col_order]

#change types (the hard way) for writing
loc_qual['LastYear'] = loc_qual['LastYear'].astype('int64')
loc_qual['ZIP'] = loc_qual['ZIP'].astype('int64')
loc_qual['citycode'] = loc_qual['citycode'].astype('int64')
loc_qual['FipsCounty'] = loc_qual['FipsCounty'].astype('int64')
loc_qual['CBSA'] = loc_qual['CBSA'].astype('int64')
loc_qual['BEH_LOC'] = loc_qual['BEH_LOC'].astype('int64')
loc_qual['BEH_ID'] = loc_qual['BEH_ID'].astype('int64')
loc_qual['backfill_flag'] = loc_qual['backfill_flag'].astype('int64')


#Change again to str stype for writing
loc_qual.reset_index(drop=False, inplace=True)
for col in loc_qual.columns:
    loc_qual[col] = loc_qual[col].astype('object')

loc_qual.reset_index(inplace=True, drop=False)

loc_qual.to_csv(writepath, sep='\t', index=False)

