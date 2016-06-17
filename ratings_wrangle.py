filename = "E:\NETS_Clients2013ASCI\NETS2013_Ratings.txt"

def splitlist(numsplits,list):
    l = [0]*numsplits
    for i in xrange(numsplits):
        l[i] = list[i::numsplits]
    return l

def w2l(numyrs):
    with open('temp.txt') as f, open('out.csv', 'w') as f2:
        f2.write('Key, Year, A, B,\n')
        for i, line in enumerate(f):
            if i == 0:
                strip = line.strip().split('\t')
                _, headers = strip[0], strip[1:]
                headers = ['19' + h[1:] for h in headers]
            else:
                strip = line.strip().split('\t')
                key, rest = strip[0], strip[1:]
                restsplit = splitlist(numyrs, rest) # [rest[i:i+numvars] for i in xrange(0, len(rest),numvars)]#
                for year, values in zip(headers, restsplit):
                    f2.write(','.join([key, year, ','.join(values)]) + '\n')

if __name__ == '__main__':
    w2l(3)
