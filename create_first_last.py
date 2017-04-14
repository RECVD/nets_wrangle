from itertools import izip
import functions as fx

# Filenames
add99name = "E:\NETSDatabase2014\NETS2014_AddressSpecial90to99.txt"
add14name = "E:\NETSDatabase2014\NETS2014_AddressSpecial00to14.txt"
writename = "E:\NETSDatabase2014_wrangled\NETS2014_FirstLast.csv"

with open(add99name) as f90, open(add14name) as f14, open(writename, 'w') as writefile:
    # Match up each index with it's year based on the first line
    line1_90 = f90.readline().strip().split('\t')[1:]
    line1_14 = f14.readline().strip().split('\t')[1:]
    line1 = line1_90 + line1_14

    # Get the 4 digit year of each header and write as a new list for reference
    addyear = fx.make_fullyear(line1, ['Address', 'City', 'State', 'ZIP', 'CityCode', 'FipsCounty', 'CBSA'])
    headers = [thing[-4:] for thing in addyear]

    # Write first line of the new file
    writefile.write('DunsNumber, FirstYear, LastYear\n')

    for line90, line14 in izip(f90, f14):
        # Separate out the duns
        line90_list = line90.split('\t')
        duns = line90_list[0]

        line90_list = line90_list[1:]
        line14_list = line14.split('\t')[1:]

        # Get rid of newline figures and replace with empty strings
        line90_list[-1] = line90_list[-1].replace('\n', '')
        line14_list[-1] = line14_list[-1].replace('\n', '')
        # Combine
        line = line90_list + line14_list

        # Find the first and last non-empty index
        firstyear_index = next(i for i, j in enumerate(line) if j)
        lastyear_index = len(line) - 1 - next(i for i, j in enumerate(reversed(line)) if j)

        # Reference back to the years in headers
        firstyear = headers[firstyear_index]
        lastyear = headers[lastyear_index]

        writefile.write(duns + ',' +  firstyear + ',' + lastyear + ',\n')
