import pandas as pd
import cProfile
from Tkinter import Tk  # file selection through GUI
from tkFileDialog import askopenfilename  # ^^

while True:
    outpath = raw_input("Please input full path to .txt file for writing\n")
    if outpath[-4:] != '.txt':
        print "\nPlease enter a .txt file extension"
    else:
        break


def readfile():
    while True:
        try:
            Tk().withdraw()
            filename = askopenfilename()
            SIC_it = pd.read_table(filename, iterator=True, chunksize=100)  # remove hard coded chunksize later
            SIC_it.get_chunk().columns  # simple check for validity of iterator, lots of overhead, bad for the future
            break
        except Exception:
            print "Not a valid Tab-Delim Text File"

    return SIC_it


# column name definitions rename some cols.  Ex:  SIC92 -> 1992
colnames = ['DunsNumber', 'SIC2', 'SIC3', 'SIC4', 'SIC6', 'SIC8', 'SIC8_2', 'SIC8_3', 'SIC8_4', 'SIC8_5', 'SIC8_6',
            '1990',
            '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003',
            '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', 'SICChange', 'Industry',
            'IndustryGroup']

# Set values for melting later
ids = ['DunsNumber', 'SIC8', 'SICChange', 'Industry', 'IndustryGroup']
values = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
          '2003',
          '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013']


def BEH(group):
    list_sic = list(group['SIC'])
    common = max(set(list_sic), key=list_sic.count)
    BEH_LargestPercent = round((float(list_sic.count(common)) / len(list_sic) * 100), 2)

    if BEH_LargestPercent >= 75:
        BEH_SIC = common
    else:
        BEH_SIC = group['SIC8']

    return pd.DataFrame({'DunsNumberC': group['DunsNumber'],
                         'Common_SIC': common,
                         'BEH_LargestPercent': BEH_LargestPercent,
                         'BEH_SIC': BEH_SIC})


def main():
    sic_it = readfile()
    for chunk in sic_it:
        try:
            chunk.columns = colnames
        except ValueError:
            print 'File is not correctly formatted SIC File'
            break

        melted = pd.melt(chunk, id_vars=ids, value_vars=values,
                         var_name="Year", value_name="SIC").dropna(subset={"SIC"})  # melt from wide to long format
        melted['SIC'] = melted['SIC'].astype(int)
        melted.sort_values(['DunsNumber', 'Year'], inplace=True)  # sort by DUNS and Year
        melted.reset_index(inplace=True, drop=True)  # drop added index

        grouped = melted.groupby("DunsNumber")
        melted = pd.concat([melted, grouped.apply(BEH)], axis=1)  # Calc BEH_SIC, BEH_Largest_percent
        melted.drop('DunsNumberC', axis=1, inplace=True)
        melted.to_csv(outpath, sep='\t')

        break  # end for testing purposes


cProfile.run('main()', 'profile.prof')
