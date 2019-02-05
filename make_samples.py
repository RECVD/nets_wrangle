import os
import pandas as pd

# All filenames
path = "C:\Users\jc4673\Documents\NETS\NETS2014_RAW"

# Create generator for all text files
files = (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))

for name in files:
    print(name)
    # print(pd.read_table(path + "\\" + name, nrows=10))