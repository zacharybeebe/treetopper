from treetopper.log import Log
from treetopper._constants import (
    math,
    TAPER_EQ_COEF,
    TAPER_EQ
)


class TimberQuick(object):
    """TimberQuick is a class that will virtually cruise a tree based on it's
       species, DBH, total height and plot factor. For fixed-area plots use the negative inverse of the plot size (1/30th ac = -30),
       for variable-area plots use the Basal Area Factor (BAF) (40 BAF = 40).

       Preferred Log Length and Minimum Log Length are needed
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

    def __init__(self, plot_factor: float, species: str, dbh: float, total_height: int,
                 preferred_log_length: int = 40, minimum_log_length: int = 16):
        self.plot_factor = float(plot_factor)
        self.species = str(species).upper()
        self.dbh = float(dbh)
        self.height = int(total_height)

        self.pref_log = int(preferred_log_length)
        self.min_log = int(minimum_log_length)

        self.hdr = self.height / (self.dbh / 12)
        self.ba = self.dbh ** 2 * 0.005454
        self.rd = self.ba / math.sqrt(self.dbh)

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
        """Returns the diameter inside bark (DIB) at any given stem height"""
        return math.floor(TAPER_EQ[self.species](self.dbh, self.height, stem_height, *TAPER_EQ_COEF[self.species]))

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
           at 75% of the total height. The starting merch height is found when the check DIB equals the Merch DIB.
           All DIBs are rounded down to their floor values, so there may be multiple stem heights with the same DIB integer.
           The final merch height will be the top extent of this stem height range"""
        notcheck = True
        floor = 0
        ceiling = self.height
        chkhgt = (ceiling - floor) // 4 * 3

        while notcheck:
            chkdib = self.get_any_dib(chkhgt)
            if chkdib == self.merch_dib:
                for i in range(1, 21):
                    chkhgt += 1
                    chkdib_after = self.get_any_dib(chkhgt)

                    if chkdib_after != chkdib:
                        notcheck = False
                        break
            elif chkdib > self.merch_dib:
                floor = chkhgt
                chkhgt = ceiling - ((ceiling - floor) // 2)
            else:
                ceiling = chkhgt
                chkhgt = ceiling - ((ceiling - floor) // 2)
                       
        return chkhgt - 1

    def _get_volume_and_logs(self):
        """Method for cruising the tree, this will determine the stem heights and lengths of the logs, which are sent to
           the Log Class for volume calculations, return a dictionary of the logs by log number"""
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
           self._calc_log_stem, if self._calc_log_stem returns None, all logs have been found and iteration is complete"""
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

    @staticmethod
    def _calc_log_length(previous_log_stem_height, current_log_stem_height):
        """Returns a log length in multiples of 2 (24, 26, 28... feet)"""
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
       and Cubic Feet (based on the Two-End Conic Cubic Foot Rule) are calculated.

       For inventories, this class is meant to be added to the Plot Class using the Plot Class method of add_tree"""

    def __init__(self, plot_factor: float, species: str, dbh: float, total_height: int):
        self.plot_factor = float(plot_factor)
        self.species = str(species).upper()
        self.dbh = float(dbh)
        self.height = int(total_height)

        self.hdr = self.height / (self.dbh / 12)
        self.ba = self.dbh ** 2 * 0.005454
        self.rd = self.ba / math.sqrt(self.dbh)

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
        """Adds Log Class to the logs dictionary of TimberFull and recalculates the tree's volumes and
           volume-related metrics"""
        if not self.logs:
            self.logs[1] = Log(self, stem_height, length, grade=grade.upper(), defect_pct=defect)
        else:
            num = max(self.logs) + 1
            self.logs[num] = Log(self, stem_height, length, grade=grade.upper(), defect_pct=defect)
        self._calc_volume_and_logs()

    def get_any_dib(self, stem_height):
        """Returns the diameter inside bark (DIB) at any given stem height"""
        return math.floor(TAPER_EQ[self.species](self.dbh, self.height, stem_height, *TAPER_EQ_COEF[self.species]))

    def _calc_volume_and_logs(self):
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
    # tree_data_list -> [Plot Factor, Species, DBH, Total Height]

    def display_tree_attrs(tree):
        print('Tree Attributes')
        for attr in tree.__dict__:
            print(f'\t{attr}: {tree.__dict__[attr]}')
        print('\nTree Logs from Log class:')
        for lnum in tree.logs:
            print(f'\tLog # {lnum} Attributes:')
            log = tree.logs[lnum]
            for l_attr in log.__dict__:
                print(f'\t\t{l_attr}: {log.__dict__[l_attr]}')
            print()


    tree_data_list = [33.3, 'PP', 32.2, 145]
    tree = TimberQuick(*tree_data_list)
    print('TREE EXAMPLE 1 - FROM TimberQuick')
    display_tree_attrs(tree)

    print('\n\n')

    tree_data_list = [40, 'DF', 25.5, 125]
    tree = TimberFull(*tree_data_list)
    tree.add_log(42, 40, 'SM', 5)
    tree.add_log(83, 40, 'S2', 0)
    tree.add_log(102, 18, 'S4', 10)

    print('TREE EXAMPLE 2 - FROM TimberFull')
    display_tree_attrs(tree)





















    



        






    

