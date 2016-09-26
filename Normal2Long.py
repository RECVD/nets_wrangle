import pandas as pd
import numpy as np
import json
import Tkinter as tk
import tkFileDialog as filedialog

def get_highest_cat(cat_list, rankings):
    """Function to get an exclusive category from a list of category based on its ranking"""
    rankings = [rankings[cat.strip()]['ranking'] for cat in cat_list]
    return cat_list[rankings.index(min(rankings))].strip()

# All necessary filenames
"""
filename = "C:\Users\jc4673\Documents\Columbia\NETS2013_Wrangled\NETS2013_Classifications.txt"
ranking_config = "C:/Users/jc4673/Documents/Columbia/nets_wrangle/category_ranking/ranking_config.json"
writepath = 'C:\Users\jc4673\Documents\Columbia\NETS2013_Wrangled\NETS2013_Classifications_Long.txt'
"""

filename = filedialog.askopenfilename(title='Select File')
writepath = filedialog.askdirectory(title='Select File to Write To') + '/NETS2013_Classifications_Long.txt'
ranking_config = filedialog.askopenfilename(title='Select Ranking JSON file')

class_df = pd.read_table(filename,  dtype={'FirstYear': int, 'LastYear': int}, chunksize=10**5)

# Open JSON business rankings file and load into a dict
with open(ranking_config) as f:
    rankings = json.load(f)

first = True  # determines whether we write to a new file or append
for class_chunk in class_df:

    # Create a list containing every individual year for this chunk
    firstyear = class_chunk['FirstYear'].tolist()
    lastyear = class_chunk['LastYear'].tolist()
    year_nested = [range(x, y+1) for x,y in zip(firstyear, lastyear)]
    year = pd.Series([item for sublist in year_nested for item in sublist])

    is_multiyear = class_chunk['YearsActive'] > 1  #  Find all multiyear businesses
    df_try = class_chunk[is_multiyear]

    # Make multiple entries for each business active for >1 year
    class_chunk2 = class_chunk.loc[np.repeat(class_chunk.index.values, class_chunk['YearsActive'])].reset_index(drop=True)

    class_chunk2['Year'] = year
    class_chunk2['Year'] = class_chunk2['Year'].astype(int)


    # Drop unessecary columns and set a MultiIndex
    class_chunk2.drop(labels=['FirstYear', 'LastYear'], axis=1, inplace=True)
    class_chunk2.set_index(['DunsNumber', 'Year'], drop=True, inplace=True)

    # Clear duplicated years for businesses who changed SIC codes
    class_chunk2 = class_chunk2[~class_chunk2.index.duplicated(keep='last')]

    # Apply category rankings for mutually exclusive categories
    criterion = class_chunk2['Class'].map(lambda x: len(x) > 3)
    class_chunk2.loc[criterion, 'Class'] = class_chunk2.loc[criterion, 'Class'].apply(lambda x: get_highest_cat(x.split(';'), rankings))

    # Write to csv
    if first:
        class_chunk2.to_csv(writepath, sep='\t')
        first = False
        print('.')
    else:
        class_chunk2.to_csv(writepath, sep='\t', mode='a', header=False)
        print('.')

