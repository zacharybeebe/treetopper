import math
from treetopper._utils import (
    is_err_num
)


# TAPER EQUATION FUNCTIONS
def czaplewski(DBH, Total_Height, Stem_Height, a, b, c, d, e, f):
    Z = Stem_Height / Total_Height
    Z2 = (Stem_Height ** 2) / (Total_Height ** 2)
    I1 = int(Z < a)
    I2 = int(Z < b)
    dib = DBH * math.sqrt((c * (Z - 1)) + (d * (Z2 - 1)) + (e * ((a - Z) ** 2) * I1) + (f * ((b - Z) ** 2) * I2))
    return math.floor(dib)


def kozak1969(DBH, Total_Height, Stem_Height, a, b, c):
    Z = Stem_Height / Total_Height
    Z2 = (Stem_Height ** 2) / (Total_Height ** 2)
    dib = DBH * math.sqrt(a + (b * Z) + (c * Z2))
    return math.floor(dib)


def kozak1988(DBH, Total_Height, Stem_Height, a, b, c, d, e, f, g, h, i):
    Z = Stem_Height / Total_Height
    dib = (a * (DBH ** b) * (c ** DBH)) * ((1 - (Z ** 0.5)) / (1 - (d ** 0.5))) ** ((e * (Z ** 2)) + (f * math.log(Z + 0.001)) + (g * (Z ** 0.5)) + (h * math.exp(Z)) + (i * (DBH / Total_Height)))
    return math.floor(dib)


def wensel(DBH, Total_Height, Stem_Height, a, b, c, d, e):
    Z = (Stem_Height - 1) / (Total_Height - 1)
    X = (c + (d * DBH) + (e * Total_Height))
    dib = DBH * (a - (X * (math.log(1 - (Z ** b) * (1 - math.exp(a / X))))))
    return math.floor(dib)

# STEM TAPER EQUATION ACCORDING TO SPECIES
TAPER_EQ = {
    'SF': czaplewski,
    'GF': czaplewski,
    'NF': czaplewski,
    'WL': czaplewski,
    'LP': czaplewski,
    'PP': czaplewski,
    'DF': czaplewski,
    'WH': czaplewski,
    'RA': kozak1969,
    'BM': kozak1969,
    'SS': kozak1969,
    'ES': kozak1969,
    'AS': kozak1969,
    'WP': kozak1969,
    'RC': kozak1988,
    'CW': kozak1988,
    'JP': wensel,
    'SP': wensel,
    'WF': wensel,
    'RF': wensel,
    'RW': wensel,
    'IC': wensel
}
# STEM TAPER EQUATION COEFFICIENTS ACCORDING TO SPECIES
TAPER_EQ_COEF = {
    'SF': [0.5, 0.06, -1.742, 0.6184, -0.8838, 94.3683],
    'GF': [0.59, 0.06, -1.5332, 0.56, -0.4781, 129.9282],
    'NF': [0.59, 0.06, -1.5332, 0.56, -0.4781, 129.9282],
    'WL': [0.59, 0.06, -1.3228, 0.3905, -0.5355, 115.6905],
    'LP': [0.41, 0.06, -1.2989, 0.3693, 0.2408, 89.1781],
    'PP': [0.72, 0.06, -2.3261, 0.9514, -1.0757, 94.6991],
    'DF': [0.72, 0.12, -2.8758, 1.3458, -1.6264, 20.1315],
    'WH': [0.59, 0.06, -2.0993, 0.8635, -1.026, 91.5562],
    'RA': [0.97576, -1.22922, 0.25347],
    'BM': [0.95997, -1.46336, 0.50339],
    'SS': [0.99496, -1.98993, 0.99496],
    'ES': [0.97449, -1.42305, 0.44856],
    'AS': [0.95806, -1.33682, 0.37877],
    'WP': [0.96272, -1.37551, 0.41279],
    'RC': [1.21697, 0.84256, 1.00001, 0.3, 1.55322, -0.39719, 2.11018, -1.11416, 0.0942],
    'CW': [0.85258, 0.95297, 1.00048, 0.25, 0.73191, -0.08419, 0.19634, -0.06985, 0.14828],
    'JP': [0.82932, 1.50831, -4.08016, 0.047053, 0],
    'SP': [0.90051, 0.91588, -0.92964, 0.0077119, -0.0011019],
    'WF': [0.86039, 1.45196, -2.42273, -0.15848, 0.036947],
    'RF': [0.87927, 0.9135, -0.56617, -0.01448, 0.0037262],
    'RW': [0.955, 0.387, -0.362, -0.00581, 0.00122],
    'IC': [1.0, 0.3155, -0.34316, 0,  -0.00039283]
}

# SPECIES CODE AND SPECIES NAME
ALL_SPECIES_NAMES = {
    'DF': 'DOUGLAS-FIR',
    'WH': 'WESTERN HEMLOCK',
    'RC': 'WESTERN REDCEDAR',
    'SS': 'SITKA SPRUCE',
    'ES': 'ENGLEMANN SPRUCE',
    'SF': 'SILVER FIR',
    'GF': 'GRAND FIR',
    'NF': 'NOBLE FIR',
    'WL': 'WESTERN LARCH',
    'WP': 'WHITE PINE',
    'PP': 'PONDEROSA PINE',
    'LP': 'LODGEPOLE PINE',
    'JP': 'JEFFERY PINE',
    'SP': 'SUGAR PINE',
    'WF': 'WHITE FIR',
    'RF': 'RED FIR',
    'RW': 'COASTAL REDWOOD',
    'IC': 'INSENCE CEDAR',
    'RA': 'RED ALDER',
    'BM': 'BIGLEAF MAPLE',
    'CW': 'BLACK COTTONWOOD',
    'AS': 'QUAKING ASPEN'
}

## LOG GRADE LIST ACCORDING TO SPECIES -- LIST FORMAT: [(Minimum DIB, Minimum Log Length, Grade)]
OFFICIAL_GRADES = {
    'DF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'WH': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'RC': [(28, 16, "S1"), (20, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'SS': [(24, 12, "S1"), (20, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'ES': [(24, 17, "P3"), (20, 16, "S1"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'SF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'GF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'NF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'WL': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'WP': [(24, 17, "P3"), (20, 16, "S1"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'PP': [(24, 12, "S2"), (20, 16, "S3"), (12, 12, "S4"), (6, 1, "S5"), (5, 1, "S6"), (1, 1, 'UT')],
    'LP': [(24, 17, "P3"), (20, 16, "S1"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'JP': [(24, 12, "S2"), (20, 16, "S3"), (12, 12, "S4"), (6, 1, "S5"), (5, 1, "S6"), (1, 1, 'UT')],
    'SP': [(24, 12, "S2"), (20, 16, "S3"), (12, 12, "S4"), (6, 1, "S5"), (5, 1, "S6"), (1, 1, 'UT')],
    'WF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'RF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'RW': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'IC': [(24, 12, "S2"), (20, 16, "S3"), (12, 12, "S4"), (6, 1, "S5"), (5, 1, "S6"), (1, 1, 'UT')],
    'RA': [(16, 8, "S1"), (12, 8, "S2"), (10, 8, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'BM': [(16, 8, "S1"), (12, 8, "S2"), (10, 8, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
    'CW': [(24, 8, "P3"), (10, 8, "S1"), (6, 8, "S2"), (5, 1, "S4"), (1, 1, 'UT')],
    'AS': [(16, 8, "S1"), (12, 8, "S2"), (10, 8, "S3"), (5, 1, "S4"), (1, 1, 'UT')]
}

# LOG GRADE CODE AND NAME
GRADE_NAMES = {
    'P3': 'PEELER 3',
    'SM': 'SPECIAL MILL',
    'S1': 'SAW 1',
    'S2': 'SAW 2',
    'S3': 'SAW 3',
    'S4': 'SAW 4',
    'S5': 'SAW 5',
    'S6': 'SAW 6',
    'UT': 'UTILITY / PULP',
    'CR': 'CAMP RUN'
}

# SORTING HELPER FOR LOG GRADES
GRADE_SORT = {
    'P3': 0,
    'SM': 1,
    'S1': 2,
    'S2': 3,
    'S3': 4,
    'S4': 5,
    'S5': 6,
    'S6': 7,
    'UT': 8,
    'CR': 9,
    'TOTALS': 10
}

# SCRIBNER LOG LENGTH COEEFICIENTS AND FUNCTION -- KEY: VALUE -> {DIB: SCRIB COEFFICIENT}
# WHEN VALUES ARE LISTS THE COEFFICIENT DEPENDS ON LOG LENGTH (SEE _calc_scribner() IN LOG CLASS)
SCRIBNER_DICT = {
    0: 0.0, 1: 0.0, 2: 0.143, 3: 0.39, 4: 0.676, 5: 1.07, 6: [1.16, 1.249, 1.57], 7: [1.4, 1.608, 1.8],
    8: [1.501, 1.854, 2.2], 9: [2.084, 2.41, 2.9], 10: [3.126, 3.542, 3.815], 11: [3.749, 4.167, 4.499],
    12: 4.9, 13: 6.043, 14: 7.14, 15: 8.88, 16: 10.0, 17: 11.528, 18: 13.29, 19: 14.99, 20: 17.499,
    21: 18.99, 22: 20.88, 23: 23.51, 24: 25.218, 25: 28.677, 26: 31.249, 27: 34.22, 28: 36.376, 29: 38.04,
    30: 41.06, 31: 44.376, 32: 45.975, 33: 48.99, 34: 50.0, 35: 54.688, 36: 57.66, 37: 64.319, 38: 66.731,
    39: 70.0, 40: 75.24, 41: 79.48, 42: 83.91, 43: 87.19, 44: 92.501, 45: 94.99, 46: 99.075, 47: 103.501,
    48: 107.97, 49: 112.292, 50: 116.99, 51: 121.65, 52: 126.525, 53: 131.51, 54: 136.51, 55: 141.61,
    56: 146.912, 57: 152.21, 58: 157.71, 59: 163.288, 60: 168.99, 61: 174.85, 62: 180.749, 63: 186.623,
    64: 193.17, 65: 199.12, 66: 205.685, 67: 211.81, 68: 218.501, 69: 225.685, 70: 232.499, 71: 239.317,
    72: 246.615, 73: 254.04, 74: 261.525, 75: 269.04, 76: 276.63, 77: 284.26, 78: 292.5, 79: 300.655,
    80: 308.97, 81: 317.36, 82: 325.79, 83: 334.217, 84: 343.29, 85: 350.785, 86: 359.12, 87: 368.38,
    88: 376.61, 89: 385.135, 90: 393.98, 91: 402.499, 92: 410.834, 93: 419.166, 94: 428.38, 95: 437.499,
    96: 446.565, 97: 455.01, 98: 464.15, 99: 473.43, 100: 482.49, 101: 491.7, 102: 501.7, 103: 511.7,
    104: 521.7, 105: 531.7, 106: 541.7, 107: 552.499, 108: 562.501, 109: 573.35, 110: 583.35, 111: 594.15,
    112: 604.17, 113: 615.01, 114: 625.89, 115: 636.66, 116: 648.38, 117: 660.0, 118: 671.7, 119: 683.33,
    120: 695.011
}

# LOG LENGTH TITLES AND RANGES
LOG_LENGTHS = {
    '<= 10 feet': (1, 10),
    '11 - 20 feet': (11, 20),
    '21 - 30 feet': (21, 30),
    '31 - 40 feet': (31, 40),
    '> 40 feet': (41, 999)
}


# CHECK IF SPECIES CODE IS CORRECT
def is_err_species(val, row_num, col_num):
    if val == '' or val is None:
        return True, val, f'Row {row_num}, Col {col_num} Species cannot be blank'
    else:
        check_val = val.upper()
        if check_val not in ALL_SPECIES_NAMES:
            return True, val, f'Row {row_num}, Col {col_num} Incorrect Species Code ({val})'
        else:
            return False, check_val, None


# CHECK IF GRADE CODE IS CORRECT
def is_err_grade(val, row_num, col_num):
    if val == '' or val is None:
        return True, val, f'Row {row_num}, Col {col_num} Grade cannot be blank if Log Length is filled'
    else:
        check_val = val.upper()
        if check_val not in GRADE_NAMES:
            # Check Reverse "2S" --> "S2"
            check_reverse = check_val[::-1]
            if check_reverse in GRADE_NAMES:
                return False, check_reverse, None
            else:
                return True, val, f'Row {row_num}, Col {col_num} Incorrect Grade Code ({val})'
        else:
            return False, check_val, None


# ERROR CHECKING BY LIST INDEX
SHEET_ROW_COL_CONV = {
    1: lambda val, row, col: is_err_num(val, row, col, int),
    2: lambda val, row, col: is_err_num(val, row, col, int),
    3: is_err_species,
    4: lambda val, row, col: is_err_num(val, row, col, float),
    5: lambda val, row, col: is_err_num(val, row, col, float, required=False),
    6: lambda val, row, col: is_err_num(val, row, col, int, default=40),
    7: lambda val, row, col: is_err_num(val, row, col, int, default=16)
}

SHEET_FULL_LOG_CONV = {
    0: lambda val, row, col: is_err_num(val, row, col, int),
    1: is_err_grade,
    2: lambda val, row, col: is_err_num(val, row, col, int, default=0),
    3: lambda val, row, col: is_err_num(val, row, col, int, default=0)
}

SORTED_HEADS = [['tpa', 'TPA'], ['ba_ac', 'BASAL AREA'], ['rd_ac', 'RD'], ['qmd', 'QMD'], ['vbar', 'VBAR'],
                ['avg_hgt', 'AVG HEIGHT'], ['hdr', 'HDR'], ['bf_ac', 'BOARD FEET'], ['cf_ac', 'CUBIC FEET']]

# FVS INITIAL DATA
FVS_KEYWORDS = """Database\r
DSNin\r
{DB_NAME}\r
StandSQL\r
SELECT * FROM FVS_StandInit WHERE Stand_ID = '%Stand_ID%'\r
EndSQL\r
TreeSQL\r
SELECT * FROM FVS_TreeInit WHERE Stand_ID = '%Stand_ID%'\r
EndSQL\r
END"""

GROUPS_DEFAULTS = ['All_Stands', FVS_KEYWORDS]

ACCESS_GROUPS_COLS = ['FVS_GroupAddFilesAndKeywords', [['Groups', 'VARCHAR'], ['Addfiles', 'LONGCHAR'], ['FVSKeywords', 'LONGCHAR']]]

ACCESS_STAND_COLS = ['FVS_StandInit', [['Stand_ID', 'VARCHAR'], ['Variant', 'VARCHAR'], ['Inv_Year', 'INTEGER'], ['Groups', 'LONGCHAR'],
                     ['AddFiles', 'LONGCHAR'], ['FVSKeywords', 'LONGCHAR'], ['Latitude', 'DOUBLE'], ['Longitude', 'DOUBLE'],
                     ['Region', 'INTEGER'], ['Forest', 'INTEGER'], ['District', 'INTEGER'], ['Compartment', 'INTEGER'],
                     ['Location', 'INTEGER'], ['Ecoregion', 'VARCHAR'], ['PV_Code', 'VARCHAR'], ['PV_Ref_Code', 'INTEGER'],
                     ['Age', 'INTEGER'], ['Aspect', 'DOUBLE'], ['Slope', 'DOUBLE'], ['Elevation', 'DOUBLE'], ['ElevFt', 'DOUBLE'],
                     ['Basal_Area_Factor', 'DOUBLE'], ['Inv_Plot_Size', 'DOUBLE'], ['Brk_DBH', 'DOUBLE'], ['Num_Plots', 'INTEGER'],
                     ['NonStk_Plots', 'INTEGER'], ['Sam_Wt', 'DOUBLE'], ['Stk_Pcnt', 'DOUBLE'], ['DG_Trans', 'INTEGER'],
                     ['DG_Measure', 'INTEGER'], ['HTG_Trans', 'INTEGER'], ['HTG_Measure', 'INTEGER'], ['Mort_Measure', 'INTEGER'],
                     ['Max_BA', 'DOUBLE'], ['Max_SDI', 'DOUBLE'], ['Site_Species', 'VARCHAR'], ['Site_Index', 'DOUBLE'],
                     ['Model_Type', 'INTEGER'], ['Physio_Region', 'INTEGER'], ['Forest_Type', 'INTEGER'], ['State', 'INTEGER'],
                     ['County', 'INTEGER'], ['Fuel_Model', 'INTEGER'], ['Fuel_0_25_H', 'DOUBLE'], ['Fuel_25_1_H', 'DOUBLE'],
                     ['Fuel_1_3_H', 'DOUBLE'], ['Fuel_3_6_H', 'DOUBLE'], ['Fuel_6_12_H', 'DOUBLE'], ['Fuel_12_20_H', 'DOUBLE'],
                     ['Fuel_20_35_H', 'DOUBLE'], ['Fuel_35_50_H', 'DOUBLE'], ['Fuel_gt_50_H', 'DOUBLE'], ['Fuel_0_25_S', 'DOUBLE'],
                     ['Fuel_25_1_S', 'DOUBLE'], ['Fuel_1_3_S', 'DOUBLE'], ['Fuel_3_6_S', 'DOUBLE'], ['Fuel_6_12_S', 'DOUBLE'],
                     ['Fuel_12_20_S', 'DOUBLE'], ['Fuel_20_35_S', 'DOUBLE'], ['Fuel_35_50_S', 'DOUBLE'], ['Fuel_gt_50_S', 'DOUBLE'],
                     ['Fuel_Litter', 'DOUBLE'], ['Fuel_Duff', 'DOUBLE'], ['Photo_Ref', 'INTEGER'], ['Photo_code', 'VARCHAR']]]

ACCESS_TREE_COLS = ['FVS_TreeInit', [['Stand_ID', 'VARCHAR'], ['StandPlot_ID', 'VARCHAR'], ['Plot_ID', 'DOUBLE'], ['Tree_ID', 'DOUBLE'],
                    ['Tree_Count', 'DOUBLE'], ['History', 'DOUBLE'], ['Species', 'VARCHAR'], ['DBH', 'DOUBLE'], ['DG', 'DOUBLE'],
                    ['Ht', 'DOUBLE'], ['HTG', 'DOUBLE'], ['HtTopK', 'DOUBLE'], ['CrRatio', 'DOUBLE'], ['Damage1', 'DOUBLE'],
                    ['Severity1', 'DOUBLE'], ['Damage2', 'DOUBLE'], ['Severity2', 'DOUBLE'], ['Damage3', 'DOUBLE'], ['Severity3', 'DOUBLE'],
                    ['TreeValue', 'DOUBLE'], ['Prescription', 'DOUBLE'], ['Age', 'DOUBLE'], ['Slope', 'INTEGER'], ['Aspect', 'INTEGER'],
                    ['PV_Code', 'VARCHAR'], ['TopoCode', 'DOUBLE'], ['SitePrep', 'DOUBLE']]]

SQL_GROUPS_COLS = ['FVS_GroupAddFilesAndKeywords', [['Groups', 'TEXT'], ['Addfiles', 'TEXT'], ['FVSKeywords', 'TEXT']]]

SQL_STAND_COLS = ['FVS_StandInit', [['Stand_ID', 'TEXT'], ['Variant', 'TEXT'], ['Inv_Year', 'INTEGER'], ['Groups', 'TEXT'], ['AddFiles', 'TEXT'],
                  ['FVSKeywords', 'TEXT'], ['Latitude', 'REAL'], ['Longitude', 'REAL'], ['Region', 'INTEGER'], ['Forest', 'INTEGER'],
                  ['District', 'INTEGER'], ['Compartment', 'INTEGER'], ['Location', 'INTEGER'], ['Ecoregion', 'TEXT'], ['PV_Code', 'TEXT'],
                  ['PV_Ref_Code', 'INTEGER'], ['Age', 'INTEGER'], ['Aspect', 'REAL'], ['Slope', 'REAL'], ['Elevation', 'REAL'],
                  ['ElevFt', 'REAL'], ['Basal_Area_Factor', 'REAL'], ['Inv_Plot_Size', 'REAL'], ['Brk_DBH', 'REAL'],
                  ['Num_Plots', 'INTEGER'], ['NonStk_Plots', 'INTEGER'], ['Sam_Wt', 'REAL'], ['Stk_Pcnt', 'REAL'], ['DG_Trans', 'INTEGER'],
                  ['DG_Measure', 'INTEGER'], ['HTG_Trans', 'INTEGER'], ['HTG_Measure', 'INTEGER'], ['Mort_Measure', 'INTEGER'],
                  ['Max_BA', 'REAL'], ['Max_SDI', 'REAL'], ['Site_Species', 'TEXT'], ['Site_Index', 'REAL'], ['Model_Type', 'INTEGER'],
                  ['Physio_Region', 'INTEGER'], ['Forest_Type', 'INTEGER'], ['State', 'INTEGER'], ['County', 'INTEGER'],
                  ['Fuel_Model', 'INTEGER'], ['Fuel_0_25_H', 'REAL'], ['Fuel_25_1_H', 'REAL'], ['Fuel_1_3_H', 'REAL'],
                  ['Fuel_3_6_H', 'REAL'], ['Fuel_6_12_H', 'REAL'], ['Fuel_12_20_H', 'REAL'], ['Fuel_20_35_H', 'REAL'],
                  ['Fuel_35_50_H', 'REAL'], ['Fuel_gt_50_H', 'REAL'], ['Fuel_0_25_S', 'REAL'], ['Fuel_25_1_S', 'REAL'],
                  ['Fuel_1_3_S', 'REAL'], ['Fuel_3_6_S', 'REAL'], ['Fuel_6_12_S', 'REAL'], ['Fuel_12_20_S', 'REAL'],
                  ['Fuel_20_35_S', 'REAL'], ['Fuel_35_50_S', 'REAL'], ['Fuel_gt_50_S', 'REAL'], ['Fuel_Litter', 'REAL'],
                  ['Fuel_Duff', 'REAL'], ['Photo_Ref', 'INTEGER'], ['Photo_code', 'TEXT']]]

SQL_TREE_COLS = ['FVS_TreeInit', [['Stand_ID', 'TEXT'], ['StandPlot_ID', 'TEXT'], ['Plot_ID', 'REAL'], ['Tree_ID', 'REAL'], ['Tree_Count', 'REAL'],
                 ['History', 'REAL'], ['Species', 'TEXT'], ['DBH', 'REAL'], ['DG', 'REAL'], ['Ht', 'REAL'], ['HTG', 'REAL'],
                 ['HtTopK', 'REAL'], ['CrRatio', 'REAL'], ['Damage1', 'REAL'], ['Severity1', 'REAL'], ['Damage2', 'REAL'],
                 ['Severity2', 'REAL'], ['Damage3', 'REAL'], ['Severity3', 'REAL'], ['TreeValue', 'REAL'], ['Prescription', 'REAL'],
                 ['Age', 'REAL'], ['Slope', 'INTEGER'], ['Aspect', 'INTEGER'], ['PV_Code', 'TEXT'], ['TopoCode', 'REAL'],
                 ['SitePrep', 'REAL']]]








