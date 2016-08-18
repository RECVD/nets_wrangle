from os import listdir, chdir
from os.path import isfile, join
from pprint import pprint

dirpath = 'C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI'
writepath = r'C:\Users\jc4673\Documents\Columbia\nets_wrangle\all_columns\all_columns.txt'

chdir(dirpath)

#  open all the NETS text files and read into a dictionary
#  key = Filename, value = columns
coldict= dict()
for filepath in listdir(dirpath):
    with open(filepath, 'r') as f:
        coldict[filepath[:-4]] = f.readline().strip().split()

#  Open another file and write the dict values to it
with open(writepath, 'w') as f:
    for key, value in coldict.iteritems():
        f.write(key + '\t')
        f.write('\t'.join(value) + '\n')

