filename = "E:\NETS_Clients2013ASCI\NETS2013_Ratings.txt"

with open('temp.csv') as f, open('out.csv', 'w') as f2:
    f2.write('Key, Year, A, B,\n')
    for i, line in enumerate(f):
        if i == 0:
            strip = line.strip().split(',')
            _, headers = strip[0], strip[1:]
            headers = [(h[0], '19' + h[1:]) for h in headers]
        else:
            strip = line.strip().split(',')
            key, rest = strip[0], strip[1:]
            resta = rest[::2]
            restb = rest[1::2]
            for (a, year), valuea,valueb in zip(headers, resta, restb):
                f2.write(','.join([key, year, valuea, valueb]) + '\n')


