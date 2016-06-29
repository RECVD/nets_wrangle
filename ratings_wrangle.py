from __future__ import print_function
from itertools import chain
import time

class Reader:
    def __init__(self, filepath, delim_type, line_limit):
        self.filepath = filepath
        self.decades = ('0', '1', '9') #decade in YYYY date format
        self.line_limit = line_limit

        if delim_type == ',' or delim_type.lower() == 'comma':
            self.delim_type = ','
        elif delim_type.lower() == 'tab':
            self.delim_type = '\t'
        else: raise TypeError('Invalid delimiter: please enter "tab" or ","\n')
        self.open_file()
        self.f2 = open('out.txt', 'w')

    def open_file(self):
        self.f = open(self.filepath)

    def splitlist(self, numsplits, l, ratings):
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
                yield l[i:i + numsplits]

        else:
            inc = listlen / numsplits  # num to increment by
            k = inc
            for j in range(0, inc):
                indices = [j, j + k, j + k + 1]
                k = k + 1
                yield [l[j] for j in indices]

    def remove_duplicates(self, seq):
        """Order-Preserving method of removing duplicates from an iterable """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def read_line(self, strip=True):
        """Read a single line and return as a string"""
        if strip:
            return self.f.readline().strip().split(self.delim_type)
        else:
            return self.f.readline().split(self.delim_type)

    def get_line1(self):
        """Read and format first line and save as instance variable"""
        self.line1 = self.read_line()
        self.preyears, self.nonyears = [x for x in self.line1[1:] if x[-2] in self.decades], \
                             [x for x in self.line1[1:] if x[-2] not in self.decades]

        self.yearvars = self.remove_duplicates([x[:-2] for x in self.preyears])

        # compute column names
        colnames = list(chain.from_iterable([[self.line1[0]], self.yearvars, self.nonyears]))
        colnames.insert(1, 'Year')  # add 'Year" as second element

        return self.delim_type.join(colnames) + '%s \n' % self.delim_type

    def set_attributes(self):
        self.year_indices = [self.line1.index(x) for x in self.preyears]
        self.nonyear_indices = [self.line1.index(x) for x in self.nonyears]

        allyears = ['19' + h[-2:] if h[-2] == '9' else '20' + h[-2:] for h in self.preyears]  # convert to 'YYYY' format
        self.unique_years = self.remove_duplicates(allyears)

        # Do we need to deal with the funky formatting in the ratings table?
        if len(allyears) > 24 and allyears[0] != allyears[1]:
            self.ratings = True
        else:
            self.ratings = False

        self.num_all_years = len(allyears)  # number of total year-based columns
        self.numw2l = self.num_all_years / len(self.unique_years)  # number of vars to go from wide to long

    def wide_to_long(self, line_limit):
        for i in xrange(line_limit):
            strip = self.read_line()
            if not strip:  # until there are no lines left
                break
            try:
                key, time, nontime = strip[0], [strip[i] for i in self.year_indices], [
                    [strip[i] for i in self.nonyear_indices]] * self.num_all_years  # separate key from the rest of the line
            except IndexError:  # caused by a line having only a key or not enough values, pad it with empty vals
                padding = ["" for i in range(len(self.line1) - len(strip))]
                padded = strip + padding
                key, time, nontime = padded[0], [padded[i] for i in self.year_indices], [
                    [padded[i] for i in self.nonyear_indices]] * self.num_all_years

            timesplit = self.splitlist(self.numw2l, time, self.ratings)  # split into equal lists

            for year, timevals, nontimevals in zip(self.unique_years, timesplit, nontime):
                if not any(timevals):  # if the long to wide values are not empty
                    continue
                else:
                    self.f2.write(self.delim_type.join([key, year, self.delim_type.join(timevals), self.delim_type.join(nontimevals)]) + '%s \n' % self.delim_type)

    def main(self):
        line1 = self.get_line1()
        self.f2.write(line1)
        self.set_attributes()
        self.wide_to_long(self.line_limit)

if __name__ == '__main__':
    filename = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_Sales.txt"
    a = Reader(filename,'tab', 10**3)
    t0 = time.time()
    a.main()
    t1 = time.time()
    print(t1-t0)
