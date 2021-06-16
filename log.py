from _constants import (math,
                        GRADE_NAMES,
                        LOG_LENGTHS,
                        OFFICIAL_GRADES,
                        SCRIBNER_DICT)



class Log(object):
    """Log Class calculates the volume of an individual log from the Timber Classes. If coming from
       the TimberQuick class, it will also calculate the grade of the log"""

    def __init__(self, timber, stem_height: int, length: int, defect_pct: int = 0, grade: str = None):
        self.tree = timber
        self.stem_height = stem_height
        self.length = length
        self.defect = defect_pct

        self.species = self.tree.species
        self.lpa = self.tree.tpa

        self.top_dib = self._calc_top_dib()
        if grade:
            self.grade = grade
        else:
            self.grade = self._calc_log_grade()
        self.scrib = self._calc_scribner()
        self.bf = self._calc_board_feet()
        self.cf = self._calc_cubic_feet()

        self.bf_ac = self.bf * self.lpa
        self.cf_ac = self.cf * self.lpa


        self.grade_name = GRADE_NAMES[self.grade]
        self.length_range = self._get_length_range()


    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]

    def _get_length_range(self):
        """Gets the length range that the logs length is in, this is used for the Stand Class' report methods"""
        for rng in LOG_LENGTHS:
            if LOG_LENGTHS[rng][0] <= self.length <= LOG_LENGTHS[rng][1]:
                return rng

    def _calc_top_dib(self):
        """Uses the Timber Class' stem taper equation to calculate the top diameter inside bark (DIB) of the log
           from the stem_height argument"""
        return int(math.floor(self.tree.equation(self.tree.dbh, self.tree.height, self.stem_height, **self.tree.coef[1])))

    def _calc_log_grade(self):
        """Used when the Timber Class is TimberQuick, it will get the grade of the log based on species, minimum log lengths,
           and minimum log top DIBs set forth in the Official Rules for the Log Scaling and Grading Bureaus"""
        for i in OFFICIAL_GRADES[self.species]:
            if self.top_dib >= i[0] and self.length >= i[1]:
                return i[2]

    def _calc_board_feet(self):
        """Returns the board feet of the log based on log length and the corresponding Scribner coefficient"""
        return math.floor(self.length * self.scrib * (1 - (self.defect / 100)))

    def _calc_cubic_feet(self):
        """Return the cubic feet of the log based on the Two-End Conic Cubic Foot Rule"""
        if self.length < 17:
            x = self.length * 0.67
        else:
            x = self.length + 1
        return ((.005454 * x) * (((2 * ((self.top_dib + 0.7) ** 2)) + (2 * (self.top_dib + 0.7))) / 3)) * (1 - (self.defect / 100))

    def _calc_scribner(self):
        """Return the Scribner coefficient for board foot calculation based on log length and log top DIB"""
        if self.top_dib in range(6, 12):
            if 0 < self.length < 16:
                return SCRIBNER_DICT[self.top_dib][0]
            elif 16 <= self.length < 32:
                return SCRIBNER_DICT[self.top_dib][1]
            else:
                return SCRIBNER_DICT[self.top_dib][2]
        else:
            return SCRIBNER_DICT[self.top_dib]


