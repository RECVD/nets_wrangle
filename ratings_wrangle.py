import numpy as np
import pandas as pd
import itertools as it
import time


# hard coded portion for testing, JSON later

filename = "E:\NETS_Clients2013ASCI\NETS2013_Ratings.txt"

dnbr_rating_names = ['DunsNumber', 'DnBRating90', 'DnBRating91', 'DnBRating92', 'DnBRating93', 'DnBRating94',
                     'DnBRating95', 'DnBRating96', 'DnBRating97', 'DnBRating98', 'DnBRating99', 'DnBRating00',
                     'DnBRating01', 'DnBRating02', 'DnBRating03', 'DnBRating04', 'DnBRating05', 'DnBRating06',
                     'DnBRating07', 'DnBRating08', 'DnBRating09', 'DnBRating10', 'DnBRating11', 'DnBRating12',
                     'DnBRating13']

paydexmax_names = ['DunsNumber', 'PayDexMax90', 'PayDexMax91', 'PayDexMax92', 'PayDexMax93', 'PayDexMax94',
                   'PayDexMax95', 'PayDexMax96', 'PayDexMax97', 'PayDexMax98', 'PayDexMax99', 'PayDexMax00',
                   'PayDexMax01', 'PayDexMax02', 'PayDexMax03', 'PayDexMax04', 'PayDexMax05', 'PayDexMax06',
                   'PayDexMax07', 'PayDexMax08', 'PayDexMax09', 'PayDexMax10', 'PayDexMax11', 'PayDexMax12',
                   'PayDexMax13']

paydexmin_names = ['DunsNumber', 'PayDexMin90', 'PayDexMin91', 'PayDexMin92', 'PayDexMin93', 'PayDexMin94',
                   'PayDexMin95', 'PayDexMin96', 'PayDexMin97', 'PayDexMin98', 'PayDexMin99', 'PayDexMin00',
                   'PayDexMin01', 'PayDexMin02', 'PayDexMin03', 'PayDexMin04', 'PayDexMin05', 'PayDexMin06',
                   'PayDexMin07', 'PayDexMin08', 'PayDexMin09', 'PayDexMin10', 'PayDexMin11', 'PayDexMin12',
                   'PayDexMin13']
melt_values = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
               '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013']

# new column names that include year format YYYY for standardization
new_colnames = [0]* len(dnbr_rating_names)
for i, x in enumerate(dnbr_rating_names): #skip Duns(index for pd) and start at first year
    if x[-2] == '9':
        new_colnames[i] = '19' + x[-2:]
    elif x[-2] == '0' or x[-2] == '1':
        new_colnames[i] = '20' + x[-2:]
    else: new_colnames[i] = x


while True:
    outpath = raw_input("Please input full path to .txt file for writing\n")
    if outpath[-4:] != '.txt':
        print("\nPlease enter a .txt file extension")
        outpath = raw_input("Please input full path to .txt file for writing\n")
    else:
        break


def readfile():
    while True:
        try:
            # remember to remove hard coded chunk size later
            dnbr_rating_it = pd.read_table(filename, iterator=True, usecols=dnbr_rating_names, chunksize=1000)
            paydexmax_it = pd.read_table(filename, iterator=True, usecols=paydexmax_names, chunksize=1000)
            paydexmin_it = pd.read_table(filename, iterator=True, usecols=paydexmin_names, chunksize=1000)
            break

        except Exception:
            print "Not a valid tab-delimited text file"
            break
    return dnbr_rating_it, paydexmax_it, paydexmin_it


def main():
    dnbr_rating_it, paydexmax_it, paydexmin_it = readfile()
    for (dnbr_chunk, paydexmax_chunk, paydexmin_chunk) in it.izip(dnbr_rating_it, paydexmax_it, paydexmin_it):

        # rename column names to have year in format YYYY
        dnbr_chunk.columns = new_colnames
        paydexmax_chunk.columns = new_colnames
        paydexmin_chunk.columns = new_colnames

        dnbr_chunk.replace(to_replace='-- ', value=np.nan, inplace=True) # replace "--" that appear in original text file with NaN

        # Long to wide for dnbr, paydexmax and paydexmin
        melted_dnbr = pd.melt(dnbr_chunk, id_vars=['DunsNumber'], value_vars=melt_values,
                         var_name="Year", value_name="DnBRating").set_index(['DunsNumber', 'Year'])
        melted_dexmax = pd.melt(paydexmax_chunk, id_vars=['DunsNumber'], value_vars=melt_values,
                               var_name="Year", value_name="PayDexMin").set_index(['DunsNumber', 'Year'])
        melted_dexmin = pd.melt(paydexmin_chunk, id_vars=['DunsNumber'], value_vars=melt_values,
                           var_name="Year", value_name="PayDexMax").set_index(['DunsNumber', 'Year'])

        join1 = melted_dnbr.join(melted_dexmax, how='outer')
        joined = join1.join(melted_dexmin, how='outer')
        joined.dropna(inplace=True, how='all')

        joined.to_csv(outpath, sep='\t')

        break  # end for testing purposes



if __name__ == "__main__":
    t0 = time.clock()
    main()
    print time.clock() - t0