import pandas as pd
import tables

infile = 'C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\SIC_transformed.txt'

sic_df = pd.read_table(infile)
print(infile.columns)

