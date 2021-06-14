from _constants import *
from log import Log


##### TIMBER CLASS
class TimberQuick(object):
    def __init__(self, species: str, dbh: float, total_height: int, plot_factor: float, preferred_log_length=40, minimum_log_length=16):
        self.species = str(species).upper()
        self.dbh = float(dbh)
        self.height = int(total_height)
        self.plot_factor = float(plot_factor)
        self.pref_log = preferred_log_length
        self.min_log = minimum_log_length

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
        return math.floor(self.equation(self.dbh, self.height, stem_height, **self.coef[1]))

    def _get_tpa_ba_ac_rd_ac(self):
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
        # Form Percent is the percent of DIB at the Form Height feet above ground,
        # this percent will be rounded down for the merch DIB in inches
        # Defaults are 40% and 17 feet
        return math.floor(0.40 * self.get_any_dib(17))

    def _get_merch_height(self):
        #Divide and Conquer Algo from ground level to Total Height
        notcheck = True
        
        floor = 0
        ceiling = self.height
        chkhgt = (ceiling - floor) // 4 * 3

        while notcheck:
            chkdib = int(math.floor(self.equation(self.dbh, self.height, chkhgt, **self.coef[1])))
                
            if chkdib == int(self.merch_dib):
                #Since DIBs are rounded down there is a range of stem heights that have the same integer DIB,
                #this looks for the top most height of that range
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
        master = [1]
        for i in range(401):
            if not self._calc_log_stem(master[i]):
                break
            else:
                master.append(self._calc_log_stem(master[i]))
        return master

    def _calc_log_stem(self, previous_log_stem_height):
        min_log_check = previous_log_stem_height + self.min_log + 1

        if min_log_check > self.merch_height - 2:
            return None
        else:
            if previous_log_stem_height + 1 + self.pref_log <= self.merch_height:
                return previous_log_stem_height + self.pref_log + 1
            else:
                return self.merch_height

    def _calc_log_length(self, previous_log_stem_height, current_log_stem_height):
        return (current_log_stem_height - previous_log_stem_height - 1) // 2 * 2


class TimberFull(object):
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
        if not self.logs:
            self.logs[1] = Log(self, stem_height, length, defect_pct=defect, grade=grade.upper())
        else:
            num = max(self.logs) + 1
            self.logs[num] = Log(self, stem_height, length, defect_pct=defect, grade=grade.upper())

    def calc_volume_and_logs(self):
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
        return math.floor(self.equation(self.dbh, self.height, stem_height, **self.coef[1]))

    def _get_tpa_ba_ac_rd_ac(self):
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







        









##### EXAMPLE OF HOW TO USE LIBRARY

if __name__ == ('__main__'):
    
    #data_list = [Species Code, DBH, Total Height, Preferred Log Length, Minimum Log Length, Plot Factor]
    data_list = ['DF', 25.5, 125, 33.3]

    tree = TimberQuick(data_list[0], data_list[1], data_list[2], data_list[3])
    print(tree.bf)
    print(tree.rd_ac)
    print(tree.bf_ac)
    print(tree.logs)





















    



        






    

