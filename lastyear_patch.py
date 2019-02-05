import pandas as pd
import numpy as np

import Tkinter as tk
import tkFileDialog as filedialog


# Read in Data
loc_filename = filedialog.askopenfilename(title='Select the original Location File')
firstlast_filename = filedialog.askopenfilename(title='Select the original FirstLast File')
misc_filename = filedialog.askopenfilename(title='Select the original Misc File')
crosswalk_filename = filedialog.askopenfilename(title='Select the BEH_ID crosswalk file')
writepath =  filedialog.askdirectory(title="Select Folder to write to") + '/NETS2014_Location_Fix_patch.txt'

location = pd.read_table(loc_filename)
firstlast = pd.read_csv(firstlast_filename, usecols=['DunsNumber', 'FirstYear', 'LastYear'], index_col='DunsNumber')
misc = pd.read_table(misc_filename, usecols=['DunsNumber', 'FirstYear', 'LastYear'], index_col=['DunsNumber'])
cross = pd.read_csv(crosswalk_filename, usecols=['beh_id', 'BEH_ID_fix', 'BEH_LOC_fix'])
cross.rename(columns={'beh_id': 'BEH_ID'}, inplace=True)

# Make the switch to the correct BEH_ID using cross
loc = location.merge(cross, on='BEH_ID', how='left')
loc['BEH_ID'] = loc['BEH_ID_fix']
loc['BEH_LOC'] = loc['BEH_LOC_fix']
del loc['BEH_ID_fix']
del loc['BEH_LOC_fix']
loc['BEH_ID'] = loc['BEH_ID'].astype('str')
loc['BEH_ID'] = loc['BEH_ID'].astype('int64')

#Some values have multiple records, and the lastyear value for all of them.  fix these in loc first
loc['ActiveYears_loc'] = loc.LastYear - loc.FirstYear
active_years_total = loc.groupby('DunsNumber').apply(lambda x: x.LastYear.iloc[-1] - x.FirstYear.iloc[0])
active_years_sum = loc.groupby('DunsNumber').ActiveYears_loc.sum()
compare = pd.concat([active_years_total, active_years_sum], axis=1)
compare.columns = ['ActiveYears_total', 'ActiveYears_sum']
bad_duns = compare[compare['ActiveYears_total'] != compare['ActiveYears_sum']].index.tolist()
loc.set_index(['DunsNumber', 'FirstYear'], inplace=True)
loc_bad = loc.reindex(bad_duns, level=0)
loc_bad.reset_index(drop=False, inplace=True)

shift = lambda x: x['FirstYear'].shift(-1).combine_first(x['LastYear'])
x = loc_bad.groupby('DunsNumber').apply(shift).tolist()
loc_bad['LastYear'] = x
loc_bad.set_index(['DunsNumber', 'FirstYear'], inplace=True)
loc = loc_bad.combine_first(loc)
loc['LastYear'] = loc['LastYear'].astype('int64')


# Isolate bad LastYears from Misc and FirstLast, then subset Loc
firstlast.rename(columns={'LastYear': 'LastYear_Master'}, inplace=True)
firstlast['LastYear'] = misc['LastYear']
messedup_last = firstlast[(firstlast['LastYear'] != firstlast['LastYear_Master'])]
messedup_last_duns = messedup_last.index.tolist()
mask = loc.index.isin(messedup_last_duns, level=0)
wrong_loc_lastyear = loc[mask]

# Replace bad LastYears with Good Ones
wrong_loc_lastyear.reset_index(drop=False, inplace=True)
wrong_loc_last = wrong_loc_lastyear.groupby('DunsNumber').last()
wrong_loc_lastyear.set_index(['DunsNumber', 'FirstYear'], inplace=True)
wrong_loc_last['LastYear'] = messedup_last['LastYear_Master']
wrong_loc_last.set_index('FirstYear', append=True, inplace=True)

#Move corrected values into the larger "messed up" df
corrected_loc_last = wrong_loc_last.combine_first(wrong_loc_last)

#Move larger "messed up" df into the full df
new_loc = corrected_loc_last.combine_first(loc)

# Fix dtypes
dtypes = loc.dtypes.combine_first(corrected_loc_last.dtypes)
for k, v in dtypes.iteritems():
    new_loc[k] = new_loc[k].astype(v)

# Isolate bad FirstYears from Misc and FirstLast, then subset Loc and Integrate
firstlast.rename(columns={'FirstYear': 'FirstYear_Master'}, inplace=True)
firstlast['FirstYear'] = misc['FirstYear'] + 1

messedup_first = firstlast[firstlast['FirstYear'] != firstlast['FirstYear_Master']]
messedup_first_duns = messedup_first.index.tolist()

mask = loc.index.isin(messedup_first_duns, level=0)
wrong_loc_firstyear = loc[mask]

# Replace bad FirstYears with Good Ones
wrong_loc_firstyear.reset_index(drop=False, inplace=True)

wrong_loc_first = wrong_loc_firstyear.groupby('DunsNumber').first()
wrong_loc_firstyear.set_index(['DunsNumber', 'FirstYear'], inplace=True)
wrong_loc_first['FirstYear'] = messedup_first['FirstYear_Master']
wrong_loc_first.set_index('FirstYear', append=True, inplace=True)

#Move corrected values into the larger "messed up" df
corrected_loc_first = wrong_loc_first.combine_first(wrong_loc_first)

#Move larger "messed up" df into the full df (already updated from 'LastYear')
new_loc = corrected_loc_first.combine_first(new_loc)

# Fix dtypes
dtypes = loc.dtypes.combine_first(corrected_loc_first.dtypes)
for k, v in dtypes.iteritems():
    new_loc[k] = new_loc[k].astype(v)


# Recalculate YearsActive
new_loc['YearsActive'] = new_loc['LastYear'] - new_loc.index.get_level_values(1)


# Drop Problematic Duplicates
# Due to some weird wrangling problems (cause TBD), some 13,000 records have been created with duplicates preventing the
# replacement of the correct FirstYear and LastYear
dupes = new_loc[new_loc.YearsActive < 0] #duplicate rows with negative rows
full_dupes = new_loc[new_loc.index.isin(dupes.index.get_level_values(0), level=0)] #all rows with duns matching dupes
#drop all duplicates within full_dupes
full_dupes_cut = full_dupes.reset_index(drop=False).drop_duplicates(subset=['DunsNumber', 'Address'], keep='first').set_index(['DunsNumber', 'FirstYear'])


loc_cut = new_loc.copy()

#replace rows not in loc but not full_dupes_cut with NaN, then drop all NaN rows
loc_cut[loc_cut.index.isin(full_dupes_cut.index.get_level_values(0).tolist(), level=0)] = full_dupes_cut
loc_cut.dropna(how='all', inplace=True)


# Replace FirstYear and LastYear for remaining records of Duplicates
full_dupes_cut.reset_index(level=1, drop=False, inplace=True)

firstlast_sub = firstlast[firstlast.index.isin(full_dupes_cut.index.get_level_values(0))]
full_dupes_cut[['FirstYear', 'LastYear']] = firstlast_sub[['FirstYear_Master', 'LastYear_Master']]
full_dupes_cut.set_index('FirstYear', append=True, inplace=True)
full_dupes_cut['YearsActive'] = full_dupes_cut['LastYear'] - full_dupes_cut.index.get_level_values(1)
loc_cut[loc_cut.index.isin(full_dupes_cut.index.get_level_values(0).tolist(), level=0)] = full_dupes_cut


del loc_cut['YearsActive']
loc_cut.dropna(subset=['LastYear', 'ZIP'], inplace=True) #Two lingering bad records
loc_cut.reset_index(inplace=True)

#Fix LastYears to avoid overlap
loc_subset = loc_cut[loc_cut['BEH_LOC'] != 0]
loc_subset['LastYear'] = loc_subset['LastYear'] - 1
loc_cut = pd.concat([loc_subset, loc_cut[loc_cut['BEH_LOC'] == 0]]).sort_index()

# Fix dtypes
dtypes = location.dtypes.combine_first(loc_cut.dtypes)
for k, v in dtypes.iteritems():
    loc_cut[k] = loc_cut[k].astype(v).astype("object")

del loc_cut['ActiveYears_loc']

# Write to file
#loc_cut.reset_index(drop=False, inplace=True)
loc_cut.to_csv(writepath, sep='\t', index=False)
