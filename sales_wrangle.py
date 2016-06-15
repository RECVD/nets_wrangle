from __future__ import print_function

import pandas as pd
import itertools as it
import cProfile
from Tkinter import Tk  # file selection through GUI
from tkFileDialog import askopenfilename  # ^^


while True:
    outpath = raw_input("Please input full path to .txt file for writing\n")
    if outpath[-4:] != '.txt':
        print("\nPlease enter a .txt file extension")
    else:
        break

# column name definitions to separate iterator, both original and renamed
sales_names = ['DunsNumber','Sales90', 'Sales91', 'Sales92', 'Sales93', 'Sales94', 'Sales95', 'Sales96', 'Sales97', 'Sales98',
               'Sales99', 'Sales00', 'Sales01','Sales02','Sales03','Sales04','Sales05','Sales06','Sales07','Sales08','Sales09',
               'Sales10','Sales11','Sales12','Sales13','SalesHere','SalesGrowth','SalesGrowthPeer']

sales_rename = ['DunsNumber','1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998','1999', '2000',
                '2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','SalesHere',
                'SalesGrowth','SalesGrowthPeer']

code_names = ['DunsNumber', 'SalesC90', 'SalesC91', 'SalesC92', 'SalesC93', 'SalesC94', 'SalesC95', 'SalesC96',
              'SalesC97', 'SalesC98', 'SalesC99', 'SalesC00', 'SalesC01', 'SalesC02', 'SalesC03', 'SalesC04', 'SalesC05',
              'SalesC06', 'SalesC07', 'SalesC08', 'SalesC09', 'SalesC10', 'SalesC11', 'SalesC12', 'SalesC13', 'SalesHereC']

code_rename = ['DunsNumber', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998','1999', '2000',
               '2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013', 'SalesHereC']

def readfile():
    while True:
        try:
            Tk().withdraw()
            filename = askopenfilename()
            # filename = "E:\NETS_Clients2013ASCI\NETS2013_Sales.txt"
            sales_it = pd.read_table(filename, iterator=True, usecols=sales_names, chunksize=100)  # remove hard coded chunksize later
            salesc_it = pd.read_table(filename, iterator=True, usecols=code_names, chunksize=100)
            break
        except Exception:
            print("Not a valid Tab-Delim Text File")

    return sales_it, salesc_it

# Set values to keep and melt on, add to JSON config file later
ids_sales = ['DunsNumber', 'SalesGrowth', 'SalesGrowthPeer']
ids_c = ['DunsNumber']
values_sales = ['1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
                '2003','2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013']
values_c = ['c' + x for x in values_sales]

def main():
    sales_it, salesc_it = readfile()
    for sales_chunk, code_chunk in it.izip(sales_it, salesc_it):

        # rename column names to have year in format YYYY
        sales_chunk.columns = sales_rename
        code_chunk.columns = code_rename

        #Long to wide for both sales and codes
        melted_sales = pd.melt(sales_chunk, id_vars=ids_sales, value_vars=values_sales,
                         var_name="Year", value_name="Sales")  # melt sales from wide to long format

        melted_c = pd.melt(code_chunk, id_vars=ids_c, value_vars=values_sales,
                               var_name="Year", value_name="SalesC")  # melt code from wide to long format

        joined = pd.merge(melted_sales, melted_c, on=["DunsNumber", "Year"], how='left')
        joined = joined.dropna(subset={'Sales'}) #remove empty rows
        joined.sort_values(['DunsNumber', 'Year'], inplace=True)  # sort by DUNS and Year
        joined.reset_index(drop=True, inplace=True)

        joined.to_csv(outpath, sep='\t')

        break  # end for testing purposes


if __name__ == '__main__':
    main()
