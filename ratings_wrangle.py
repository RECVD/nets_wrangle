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


def w2l(delim_type):
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

    with open('temp.txt') as f, open('out.csv', 'w') as f2:

        strip = f.readline().strip().split(delim)
        colnames = remove_duplicates([x[:-2] if x[-2] == '9' or x[-2] == '0' else x for x in strip])
        colnames.insert(1, 'Year')
        f2.write(delim.join(colnames) + '%s \n' % delim)
        _, line1 = strip[0], strip[1:]
        headers = ['19' + h[1:] if h[-2] == '9' else '20' + h[1:] for h in line1]
        numyrs = len(set(headers))

        for i, line in enumerate(f):
            strip = line.strip().split(delim)
            key, rest = strip[0], strip[1:]
            restsplit = splitlist(numyrs, rest)
            for year, values in zip(headers, restsplit):
                f2.write(delim.join([key, year, delim.join(values)]) + '%s \n' % delim)

if __name__ == '__main__':
    w2l(',')
