filename = "E:\NETS_Clients2013ASCI\NETS2013_Ratings.txt"

def splitlist(numsplits,list):
    l = [0]*numsplits
    for i in xrange(numsplits):
        l[i] = list[i::numsplits]
    return l

def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def w2l(numyrs):
    with open('temp.txt') as f, open('out.csv', 'w') as f2:

        for i, line in enumerate(f):
            if i == 0:
                strip = line.strip().split(',')
                colnames = remove_duplicates([x[:-2] if x[-2] == '9' or x[-2] == '0' else x for x in strip])
                colnames.insert(1,'Year')
                f2.write(','.join(colnames) + ',\n')
                _, line1 = strip[0], strip[1:]
                headers = ['19' + h[1:] if h[-2] == '9' else '20' + h[1:] for h in line1]

            else:
                strip = line.strip().split(',')
                key, rest = strip[0], strip[1:]
                restsplit = splitlist(numyrs, rest)
                for year, values in zip(headers, restsplit):
                    f2.write(','.join([key, year, ','.join(values)]) + ',\n')

if __name__ == '__main__':
    w2l(4)
