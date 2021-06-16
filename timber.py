from _constants import *
from log import Log


class TimberQuick(object):
    """TimberQuick is a class that will virtually cruise a tree based on it's
       species, DBH, and total height. Preferred Log Length and Minimum Log Length are needed
       but set at the default industry standard of 40 foot preferred and 16 foot minimum.

       TimberQuick uses stem-taper equations from Czaplewski, Kozak, or Wensel
       (depending on species) to calculate the DIB (diameter inside bark) at any stem height.

       TimberQuick will instantiate the tree with common individual and per acre metrics based on the input args.

       To cruise the tree, first TimberQuick determines the merchantable DIB of the tree, this is calculated from
       40% of the DIB at a stem height of 17 feet (the FORM height). This is industry standard.

       TimberQuick then correlates that Merch DIB to a merchantable height. The tree is then split up into logs,
       based on this Merch Height with priority given to the preferred log length and if preferred log length
       cannot be achieved, then if the remaining length up to Merch Height is greater than or equal to the minimum log length,
       that final log is added.

       Log metrics are sent to the Log Class, to which their volumes in Board Feet
       (using Scribner Coefficients based on Log Length and top DIB) and Cubic Feet (based on the Two-End Conic Cubic Foot Rule).
       Log grades are determined by species, minimum log lengths and minimum top DIBs set forth by the
       Official Rules for the Log Scaling and Grading Bureaus. Log defect is always 0%

       For inventories, this class is meant to be added to the Plot Class using the Plot Class method of add_tree"""

    def __init__(self, species: str, dbh: float, total_height: int, plot_factor: float,
                 preferred_log_length: int = 40, minimum_log_length: int = 16):
        self.species = str(species).upper()
        self.dbh = float(dbh)
        self.height = int(total_height)
        self.plot_factor = float(plot_factor)
        self.pref_log = int(preferred_log_length)
        self.min_log = int(minimum_log_length)

        self.hdr = self.height / (self.dbh / 12)
        self.ba = self.dbh ** 2 * 0.005454
        self.rd = self.ba / math.sqrt(self.dbh)
        self.coef = ALL_TAPERS_DICT[self.species]
        self.equation = EQUATION_DICT[self.coef[0]]

        self.merch_dib = self._get_merch_dib()
        self.merch_height = self._get_merch_height()

        self.tpa, self.ba_ac, self.rd_ac = 0, 0, 0
        self._get_tpa_ba_ac_rd_ac()

        self.bf = 0
        self.cf = 0
        self.bf_ac = 0
        self.cf_ac = 0
        self.vbar = 0

        self.logs = self._get_volume_and_logs()

    def __getitem__(self, item):
        return self.__dict__[item]

    def get_any_dib(self, stem_height):
        """Return the diameter inside bark (DIB) at any given stem height"""
        return math.floor(self.equation(self.dbh, self.height, stem_height, **self.coef[1]))

    def _get_tpa_ba_ac_rd_ac(self):
        """Calculates the Trees per Acre, Basal Area per Acre and Relative Density per Acre
           based on the plot factor"""
        if self.plot_factor == 0:
            return
        elif self.plot_factor > 0:
            self.tpa = self.plot_factor / self.ba
            self.ba_ac = self.plot_factor
            self.rd_ac = self.tpa * self.rd
        else:
            self.tpa = abs(self.plot_factor)
            self.ba_ac = abs(self.plot_factor) * self.ba
            self.rd_ac = self.tpa * self.rd

    def _get_merch_dib(self):
        """Form Percent is the percent of DIB at the Form Height feet above ground,
           this percent will be rounded down for the merch DIB in inches.
           Industry standards are 40% and 17 feet"""
        return math.floor(0.40 * self.get_any_dib(17))

    def _get_merch_height(self):
        """Merch Height is calculated by a Divide and Conquer Algorithm with the starting check height
           at 75% of the total height. The starting merch height is found when the check height equals the Merch DIB.
           All DIBs are rounded down to their floor values, so there may be multiple stem heights with the same DIB integer.
           The final merch height will be the top extent of this stem height range"""
        notcheck = True
        floor = 0
        ceiling = self.height
        chkhgt = (ceiling - floor) // 4 * 3

        while notcheck:
            chkdib = int(math.floor(self.equation(self.dbh, self.height, chkhgt, **self.coef[1])))
                
            if chkdib == int(self.merch_dib):
                for i in range(1, 21):
                    chkhgt += 1
                    chkdib_after = int(math.floor(self.equation(self.dbh, self.height, chkhgt, **self.coef[1])))

                    if chkdib_after != chkdib:
                        notcheck = False
                        break
            elif chkdib > int(self.merch_dib):
                floor = chkhgt
                chkhgt = ceiling - ((ceiling - floor) // 2)
            else:
                ceiling = chkhgt
                chkhgt = ceiling - ((ceiling - floor) // 2)
                       
        return chkhgt - 1


    def _get_volume_and_logs(self):
        """Function for cruising the tree, this will determine the stem heights and lengths of the logs, which are sent to
           the Log Class for volume calculations"""
        stem_heights = self._calc_stem_heights()
        lengths = [self._calc_log_length(stem_heights[i-1], stem_heights[i]) for i in range(1, len(stem_heights))]
        stem_heights.pop(0)

        logs = {}
        bf = 0
        cf = 0
        for i, (stem_height, length) in enumerate(zip(stem_heights, lengths)):
            log = Log(self, stem_height, length)
            bf += log.bf
            cf += log.cf
            logs[i+1] = log

        self.bf = bf
        self.cf = cf
        self.bf_ac = self.bf * self.tpa
        self.cf_ac = self.cf * self.tpa
        self.vbar = self.bf / self.ba
        return logs

    def _calc_stem_heights(self):
        """Starting at stem height of 1 (stump height), master is updated with the log stem height calculated from
           self._calc_log_stem, if self._calc_log_stem return None, all logs have been found and iteration is complete"""
        master = [1]
        for i in range(401):
            if not self._calc_log_stem(master[i]):
                break
            else:
                master.append(self._calc_log_stem(master[i]))
        return master

    def _calc_log_stem(self, previous_log_stem_height):
        """Using the previous_log_stem_height arg, it will check if the minimum log length added to previous stem height plus
           1 foot of in-between is greater than the merch height, if it is, it will return None and no more logs can be added. If not
           it will check if the preferred log length added to the previous stem height plus 1 foot of in-between is less than
           or equal to the merch height, if it is then the new stem height is returned and a 40 foot (or user defined preferred length)
           log will added. If not then the merch height is the returned and a final log is added with a length determined by the difference
           between the merch height and previous stem height"""
        min_log_check = previous_log_stem_height + self.min_log + 1

        if min_log_check > self.merch_height - 2:
            return None
        else:
            if previous_log_stem_height + 1 + self.pref_log <= self.merch_height:
                return previous_log_stem_height + self.pref_log + 1
            else:
                return self.merch_height

    def _calc_log_length(self, previous_log_stem_height, current_log_stem_height):
        """Return a log length in multiples of 2 (24, 26, 28... feet)"""
        return (current_log_stem_height - previous_log_stem_height - 1) // 2 * 2


class TimberFull(object):
    """TimberFull is a class that will cruise a tree based on it's based on the user-cruised logs. These logs can be manually
       added to the class using the add_log method. Required arguments for add_log are stem height (int), log length (int),
       log grade (str), and log defect (int). Log defect should be the whole number value of the estimated percent defect 10% = 10.

       Like TimberQuick, TimberFull uses stem-taper equations from Czaplewski, Kozak, or Wensel
       (depending on species) to calculate the DIB (diameter inside bark) at any stem height.

       TimberFull will instantiate the tree with common individual and per acre metrics based on the input args.

       When the user adds a log using the add_log method, the log metrics are sent to the Log Class,
       to which their volumes in Board Feet (using Scribner Coefficients based on Log Length and top DIB)
       and Cubic Feet (based on the Two-End Conic Cubic Foot Rule)

       For inventories, this class is meant to be added to the Plot Class using the Plot Class method of add_tree"""

    def __init__(self, species: str, dbh: float, total_height: int, plot_factor: float):
        self.species = str(species).upper()
        self.dbh = float(dbh)
        self.height = int(total_height)
        self.plot_factor = float(plot_factor)

        self.hdr = self.height / (self.dbh / 12)
        self.ba = self.dbh ** 2 * 0.005454
        self.rd = self.ba / math.sqrt(self.dbh)

        self.coef = ALL_TAPERS_DICT[self.species]
        self.equation = EQUATION_DICT[self.coef[0]]

        self.tpa, self.ba_ac, self.rd_ac = 0, 0, 0
        self._get_tpa_ba_ac_rd_ac()

        self.bf = 0
        self.cf = 0
        self.bf_ac = 0
        self.cf_ac = 0
        self.vbar = 0

        self.logs = {}

    def __getitem__(self, item):
        return self.__dict__[item]

    def add_log(self, stem_height, length, grade, defect):
        """Adds Log Class to the logs dictionary of Timber Full and recalculates the tree's volumes and
           volume-related metrics"""
        if not self.logs:
            self.logs[1] = Log(self, stem_height, length, defect_pct=defect, grade=grade.upper())
        else:
            num = max(self.logs) + 1
            self.logs[num] = Log(self, stem_height, length, defect_pct=defect, grade=grade.upper())
        self.calc_volume_and_logs()

    def calc_volume_and_logs(self):
        """Calcuates the tree's volume and volume-related metrics based on the log volumes"""
        if not self.logs:
            return
        else:
            bf = 0
            cf = 0
            for lnum in self.logs:
                log = self.logs[lnum]
                bf += log.bf
                cf += log.cf

            self.bf = bf
            self.cf = cf
            self.bf_ac = self.bf * self.tpa
            self.cf_ac = self.cf * self.tpa
            self.vbar = self.bf / self.ba

    def get_any_dib(self, stem_height):
        """Return the diameter inside bark (DIB) at any given stem height"""
        return math.floor(self.equation(self.dbh, self.height, stem_height, **self.coef[1]))

    def _get_tpa_ba_ac_rd_ac(self):
        """Calculates the Trees per Acre, Basal Area per Acre and Relative Density per Acre
           based on the plot factor"""
        if self.plot_factor == 0:
            return
        elif self.plot_factor > 0:
            self.tpa = self.plot_factor / self.ba
            self.ba_ac = self.plot_factor
            self.rd_ac = self.tpa * self.rd
        else:
            self.tpa = abs(self.plot_factor)
            self.ba_ac = abs(self.plot_factor) * self.ba
            self.rd_ac = self.tpa * self.rd





"""EXAMPLE OF TIMBER CLASSES"""

if __name__ == ('__main__'):

    #tree_data_list -> [Species, DBH, Total Height, Plot Factor]

    tree_data_list = ['PP', 32.2, 145, 33.3]
    tree = TimberQuick(tree_data_list[0], tree_data_list[1], tree_data_list[2], tree_data_list[3])
    print(f'Tree BF: {tree.bf}')
    print(f'Tree RD/ac: {tree.rd_ac}')
    print(f'Tree BF/ac: {tree.bf_ac}')
    print(f'Tree CF/ac: {tree.cf_ac}')
    print('Tree Logs:')
    for lnum in tree.logs:
        print(f'\tLog # {lnum}:')
        log = tree.logs[lnum]
        print(f'\t\tLog Stem Height: {log.stem_height}')
        print(f'\t\tLog Length: {log.length}')
        print(f'\t\tLog Top DIB: {log.top_dib}')
        print(f'\t\tLog Grade: {log.grade}')
        print(f'\t\tLog BF: {log.bf}')
        print(f'\t\tLog CF: {log.cf}\n')

    tree2_data_list = ['DF', 25.5, 125, 40]
    tree2 = TimberFull(tree2_data_list[0], tree2_data_list[1], tree2_data_list[2], tree2_data_list[3])
    tree2.add_log(42, 40, 'SM', 5)
    tree2.add_log(83, 40, 'S2', 0)
    tree2.add_log(102, 18, 'S4', 10)
    print(f'Tree BF: {tree2.bf}')
    print(f'Tree RD/ac: {tree2.rd_ac}')
    print(f'Tree BF/ac: {tree2.bf_ac}')
    print(f'Tree CF/ac: {tree2.cf_ac}')
    print('Tree Logs:')
    for lnum in tree2.logs:
        print(f'\tLog # {lnum}:')
        log = tree2.logs[lnum]
        print(f'\t\tLog Stem Height: {log.stem_height}')
        print(f'\t\tLog Length: {log.length}')
        print(f'\t\tLog Top DIB: {log.top_dib}')
        print(f'\t\tLog Grade: {log.grade}')
        print(f'\t\tLog BF: {log.bf}')
        print(f'\t\tLog CF: {log.cf}\n')





















    



        






    

