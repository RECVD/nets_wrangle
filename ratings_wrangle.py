from __future__ import print_function

filename = "E:\NETS_Clients2013ASCI\NETS2013_Ratings.txt"

def splitlist(numsplits,list):
    """
    Split List into sub-lists of equal size whilst preserving order
    ------------
    Keyword Arguments:
    numsplits:  number of sublists to return
    list:  original list to be split
    """

    l = [0]*numsplits
    for i in xrange(numsplits):
        try:
            l[i] = list[i::numsplits]
        except IndexError as e:
            print(e.message)
    return l


def remove_duplicates(seq):
    """Order-Preserving method of removing duplicates from an iterable """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def w2l(filepath, delim_type):
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

    with open(filepath) as f, open('out.csv', 'w') as f2:

        strip = f.readline().strip().split(delim) #first line

        decades = ('0', '1', '9') #decade digit in YYYY

        #compute column names
        colnames = remove_duplicates([x[:-2] if x[-2] in decades else x for x in strip])
        colnames.insert(1, 'Year') # add 'Year" as second element
        f2.write(delim.join(colnames) + '%s \n' % delim)

        # split into time-based columns and non-time based, don't include key
        preyears, nonyears = [x for x in strip[1:] if x[-2] in decades], \
                             [x for x in strip[1:] if x[-2] not in decades]

        years = ['19' + h[1:] if h[-2] == '9' else '20' + h[1:] for h in preyears] # convert to 'YYYY' format
        numyrs = len(set(years)) # number of unique years

        for i, line in enumerate(f):
            strip = line.strip().split(delim)
            key, time, nontime = strip[0], strip[1:len(years)+1], [strip[len(years)+1:]]*len(years) #separate key from the rest of the line
            timesplit = splitlist(numyrs, time) #split into equal lists
            for year, timevals, nontimevals in zip(years, timesplit, nontime):
                f2.write(delim.join([key, year, delim.join(timevals), delim.join(nontimevals)]) + '%s \n' % delim)

if __name__ == '__main__':
    w2l(filename, ',')
