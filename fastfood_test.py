import pandas as pd
from pprint import pprint

infile = 'C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\SIC_transformed.txt'

sic_df = pd.read_table(infile)
pprint(sic_df.columns)

pprint(sic_df.groupby('Overall_Class').count()['DunsNumber'])

