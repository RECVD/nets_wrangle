import pandas as pd
import numpy as np
import json
import Tkinter as tk
import tkFileDialog as filedialog

def get_highest_cat(cat_list, rankings):
    """Function to get an exclusive category from a list of category based on its ranking"""
    rankings = [rankings[cat.strip()]['ranking'] for cat in cat_list]
    return cat_list[rankings.index(min(rankings))].strip()

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

