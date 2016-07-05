from itertools import chain
import time

class Reader:
    def __init__(self, filepath, delim_type, line_limit=0):
        self.filepath = filepath
        self.delim_type = delim_type
        self.line_limit = line_limit

        self.f = self.open_file()
        self.line_gen = self.read_all()  # create line generator

    def open_file(self):
        """Opens the file specified in 'filepath'"""
        return open(self.filepath, 'r')

    def read_all(self):
        """Generator that will yield lines in the file"""
        if self.line_limit:  # if we're not reading the whole file
            for _, line in zip(xrange(self.line_limit), self.f):
                yield line.strip().split(self.delim_type)
        else:
            for line in self.f:
                yield line.strip().split(self.delim_type)

    def close_file(self):
        self.f.close()


class Manipulator:
    def __init__(self, generator, SIC=False):
        self.decades = ('0', '1', '9') #decade in YYYY date format
        self.generator = generator

        self.line1_noformat = self.set_attributes()
        self.line1 = self.format_line1(self.line1_noformat)
        if SIC: # only for SIC files
            self.time_indices = [self.line1_noformat.index(i) for i in self.line1_noformat if i[-2] in self.decades]
            self.sic8_index = self.line1_noformat.index('SIC8')
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
        """Efficient order-preserving method of removing duplicates from an iterable """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def BEH(self, line):

        list_sic = [line[i] for i in self.time_indices] # New variable with non-time removed from the list
        list_sic = filter(None, list_sic)
        common = max(set(list_sic), key=list_sic.count)  # Most common SIC
        BEH_LargestPercent = round((float(list_sic.count(common)) / len(list_sic) * 100), 2)

        if BEH_LargestPercent >= 75:
            BEH_SIC = common
        else:
            BEH_SIC = list_sic[self.sic8_index]

        return common, BEH_LargestPercent, BEH_SIC

    def format_line1(self, line1):
        """Read and format first line and return it.  You must pass the first line as an argument.
        -------------
        Returns: Formatted First Line.
        """
        colnames = list(chain.from_iterable([[line1[0]], self.yearvars, self.nonyears]))
        colnames.insert(1, 'Year')  # add 'Year" as second element
        return colnames

    def set_attributes(self):
        """Set all attributes to be used in later manipulation functions"""
        line1 = next(self.generator) #get the first line from the generator

        self.preyears, self.nonyears = [x for x in line1[1:] if x[-2] in self.decades], \
                             [x for x in line1[1:] if x[-2] not in self.decades]
        self.yearvars = self.remove_duplicates([x[:-2] for x in self.preyears])
        self.year_indices = [line1.index(x) for x in self.preyears]
        self.nonyear_indices = [line1.index(x) for x in self.nonyears]
        allyears = ['19' + h[-2:] if h[-2] == '9' else '20' + h[-2:] for h in self.preyears]  # convert to 'YYYY' format
        self.unique_years = self.remove_duplicates(allyears)

        # Do we need to deal with the funky formatting in the ratings table?
        if len(allyears) > 24 and allyears[0] != allyears[1]:
            self.ratings = True
        else:
            self.ratings = False

        self.num_all_years = len(allyears)  # number of total year-based columns
        self.numw2l = self.num_all_years / len(self.unique_years)  # number of vars to go from wide to long

        return line1

    def wide_to_long_single(self, line):
        try:
            key, time, nontime = line[0], [line[i] for i in self.year_indices], [
                [line[i] for i in self.nonyear_indices]] * self.num_all_years  # separate key from the rest of the line
        except IndexError:  # caused by a line having only a key or not enough values, pad it with empty vals
            padding = ["" for i in range(len(self.line1) - len(line))]
            padded = line + padding
            key, time, nontime = padded[0], [padded[i] for i in self.year_indices], [
                [padded[i] for i in self.nonyear_indices]] * self.num_all_years

        timesplit = self.splitlist(self.numw2l, time, self.ratings)  # split into equal lists

        line_list = []
        for year, timevals, nontimevals in zip(self.unique_years, timesplit, nontime):
            if not any(timevals):  # if the long to wide values are not empty
                continue
            else:
                line_list.append([key] + [year] + timevals + nontimevals)

        return line_list

    def wide_to_long_all(self):
        for line in self.generator:
                line_list = self.wide_to_long_single(line)
                for single_line in line_list:
                    yield single_line


class Writer:
    def __init__(self, filepath, delim_type, generator):
        self.filepath = filepath
        self.delim_type = delim_type
        self.generator = generator

        self.f = open(self.filepath, 'w')

    def writeline(self, data_list):
        self.f.write(self.delim_type.join(data_list) + '%s \n' % self.delim_type)

    def write_all(self ):
        for line in self.generator:
            self.writeline(line)


if __name__ == '__main__':
    t0 = time.time()
    filepath = "C:\Users\jc4673\Documents\Columbia\NETS_Clients2013ASCI\NETS2013_SIC.txt"
    read = Reader(filepath, '\t', line_limit=10**3)
    manip = Manipulator(read.line_gen, SIC=True)
    nextline = next(manip.generator)
    print(nextline)
    print(manip.BEH(nextline))
    """
    a = manip.wide_to_long_all()
    write = Writer('out.txt', '\t', a)
    write.writeline(manip.line1)
    write.write_all()
    t1 = time.time()
    print t1-t0
    """

