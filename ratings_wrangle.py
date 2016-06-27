from __future__ import print_function
from itertools import chain
import time

filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"

def splitlist(numsplits,l, ratings):
    """
    Split List into sub-lists of equal size whilst preserving order
    ------------
    Keyword Arguments:
    numsplits:  number of sublists to return
    list:  original list to be split
    ratings: is the file the wonky ordering of 'ratings', very specific to this type
    """
    listlen = len(l)
    if not ratings:
        for i in range(0, listlen, numsplits):
            yield l[i:i+numsplits]

    else:
        inc = listlen/numsplits # num to increment by
        k=inc
        for j in range(0, inc):
            indices = [j, j+k, j+k+1]
            k = k+1
            yield [l[j] for j in indices]

def remove_duplicates(seq):
    """Order-Preserving method of removing duplicates from an iterable """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def w2l(filepath, delim_type, linelimit):
    """
    Convert data from wide to long format based on dated variables.
    It is assumed the last two characters of any dated variable is the last two digits of the
    year.  This works only for 90<=yr<=2019
    ----------------
    Keyword arguments:
        delim_type:  the string delimiter, either 'tab' or ','

    """
    while True:
        if delim_type.lower() == 'tab':
            delim = '\t'
            break
        elif delim_type.lower() == ',':
            delim = ','
            break
        # else: print("Please specify 'csv' or 'txt'")
        #   continue

    with open(filepath) as f, open('out.txt', 'w') as f2:

        strip1 = f.readline().strip().split(delim) #first line

        decades = ('0', '1', '9') #decade digit in YYYY

        # split into time-based columns and non-time based, don't include key
        preyears, nonyears = [x for x in strip1[1:] if x[-2] in decades], \
                             [x for x in strip1[1:] if x[-2] not in decades]

        yearvars = remove_duplicates([x[:-2] for x in preyears])

        #compute column names
        colnames = list(chain.from_iterable([[strip1[0]], yearvars, nonyears]))
        colnames.insert(1, 'Year') # add 'Year" as second element
        f2.write(delim.join(colnames) + '%s \n' % delim)

        year_i = [strip1.index(x) for x in preyears]
        nonyear_i = [strip1.index(x) for x in nonyears]

        allyears = ['19' + h[-2:] if h[-2] == '9' else '20' + h[-2:] for h in preyears] # convert to 'YYYY' format
        uyears = remove_duplicates(allyears)

        # Do we need to deal with the funky formatting in the ratings table?
        if len(allyears) > 24 and allyears[0] != allyears[1]:
            ratings = True
        else:
            ratings = False

        num_all_years = len(allyears) #number of total year-based columns
        numw2l = num_all_years/len(uyears) #number of vars to go from wide to long


        for _, line in zip(xrange(linelimit), f):
            strip = line.strip().split(delim)
            try:
                key, time, nontime = strip[0], [strip[i] for i in year_i], [[strip[i] for i in nonyear_i]]*num_all_years #separate key from the rest of the line
            except IndexError: #caused by a line having only a key or not enough values, pad it with empty vals
                padding = ["" for i in range(len(strip1)-len(strip))]
                padded = strip + padding
                key, time, nontime = padded[0], [padded[i] for i in year_i],[[padded[i] for i in nonyear_i]] * num_all_years


            timesplit = splitlist(numw2l, time, ratings) #split into equal lists

            for year, timevals, nontimevals in zip(uyears, timesplit, nontime):
                if not any(timevals): #if the long to wide values are not empty
                    continue
                else:
                    f2.write(delim.join([key, year, delim.join(timevals), delim.join(nontimevals)]) + '%s \n' % delim)


if __name__ == '__main__':
    t0 = time.time()
    w2l(filename, 'tab', 10**3)
    t1 = time.time()
    print(t1-t0)