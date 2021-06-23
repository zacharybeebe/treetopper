import math

## TAPER EQUATION FUNCTIONS
def czaplewski(DBH, Total_Height, Stem_Height, **kwargs):
    a = kwargs['a']
    b = kwargs['b']
    c = kwargs['c']
    d = kwargs['d']
    e = kwargs['e']
    f = kwargs['f']

    Z = Stem_Height / Total_Height
    Z2 = (Stem_Height ** 2) / (Total_Height ** 2)

    if Z >= a:
        I1 = 0
    else:
        I1 = 1
    if Z >= b:
        I2 = 0
    else:
        I2 = 1

    return DBH * math.sqrt((c * (Z - 1)) + (d * (Z2 - 1)) + (e * ((a - Z) ** 2) * I1) + (f * ((b - Z) ** 2) * I2))


def kozak1969(DBH, Total_Height, Stem_Height, **kwargs):
    a = kwargs['a']
    b = kwargs['b']
    c = kwargs['c']

    Z = Stem_Height / Total_Height
    Z2 = (Stem_Height ** 2) / (Total_Height ** 2)

    return DBH * math.sqrt(a + (b * Z) + (c * Z2))


def kozak1988(DBH, Total_Height, Stem_Height, **kwargs):
    a = kwargs['a']
    b = kwargs['b']
    c = kwargs['c']
    d = kwargs['d']
    e = kwargs['e']
    f = kwargs['f']
    g = kwargs['g']
    h = kwargs['h']
    i = kwargs['i']

    Z = Stem_Height / Total_Height

    return (a * (DBH ** b) * (c ** DBH)) * ((1 - (Z ** 0.5)) / (1 - (d ** 0.5))) ** ((e * (Z ** 2)) + (f * math.log(Z + 0.001)) + (g * (Z ** 0.5)) + (h * math.exp(Z)) + (i * (DBH / Total_Height)))


def wensel(DBH, Total_Height, Stem_Height, **kwargs):
    a = kwargs['a']
    b = kwargs['b']
    c = kwargs['c']
    d = kwargs['d']
    e = kwargs['e']

    Z = (Stem_Height - 1) / (Total_Height - 1)
    X = (c + (d * DBH) + (e * Total_Height))

    return DBH * (a - (X * (math.log(1 - (Z ** b) * (1 - math.exp(a / X))))))


EQUATION_DICT = {'CZA': czaplewski,
                 'KOZ69': kozak1969,
                 'KOZ88': kozak1988,
                 'WEN': wensel}

ALL_SPECIES_NAMES = {'DF': 'DOUGLAS-FIR',
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
                     'AS': 'QUAKING ASPEN'}

## LOG GRADE LIST FORMAT: [(Minimum DIB, Minimum Log Length, Grade)]
OFFICIAL_GRADES = {'DF': [(24, 17, "P3"), (16, 17, "SM"), (12, 12, "S2"), (6, 1, "S3"), (5, 1, "S4"), (1, 1, 'UT')],
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
                   'AS': [(16, 8, "S1"), (12, 8, "S2"), (10, 8, "S3"), (5, 1, "S4"), (1, 1, 'UT')]}

GRADE_NAMES = {'P3': 'PEELER 3',
               'SM': 'SPECIAL MILL',
               'S1': 'SAW 1',
               'S2': 'SAW 2',
               'S3': 'SAW 3',
               'S4': 'SAW 4',
               'S5': 'SAW 5',
               'S6': 'SAW 6',
               'UT': 'UTILITY / PULP',
               'CR': 'CAMP RUN'}

GRADE_SORT = {'P3': 0,
              'SM': 1,
              'S1': 2,
              'S2': 3,
              'S3': 4,
              'S4': 5,
              'S5': 6,
              'S6': 7,
              'UT': 8,
              'CR': 9,
              'TOTALS': 10}

##### STEM TAPER EQUATION COEFFICIENTS ACCORDING TO SPECIES
## CZAPLEWSKI ('CZA') --- KOZAK 1969 ('KOZ69') --- KOZAK 1988 ('KOZ88') --- WENSEL ('WEN')
ALL_TAPERS_DICT = {
    'SF': ['CZA', {'a': 0.5, 'b': 0.06, 'c': -1.742, 'd': 0.6184, 'e': -0.8838, 'f': 94.3683, 'g': None, 'h': None, 'i': None}],
    'GF': ['CZA', {'a': 0.59, 'b': 0.06, 'c': -1.5332, 'd': 0.56, 'e': -0.4781, 'f': 129.9282, 'g': None, 'h': None, 'i': None}],
    'NF': ['CZA', {'a': 0.59, 'b': 0.06, 'c': -1.5332, 'd': 0.56, 'e': -0.4781, 'f': 129.9282, 'g': None, 'h': None, 'i': None}],
    'WL': ['CZA', {'a': 0.59, 'b': 0.06, 'c': -1.3228, 'd': 0.3905, 'e': -0.5355, 'f': 115.6905, 'g': None, 'h': None, 'i': None}],
    'LP': ['CZA', {'a': 0.41, 'b': 0.06, 'c': -1.2989, 'd': 0.3693, 'e': 0.2408, 'f': 89.1781, 'g': None, 'h': None, 'i': None}],
    'PP': ['CZA', {'a': 0.72, 'b': 0.06, 'c': -2.3261, 'd': 0.9514, 'e': -1.0757, 'f': 94.6991, 'g': None, 'h': None, 'i': None}],
    'DF': ['CZA', {'a': 0.72, 'b': 0.12, 'c': -2.8758, 'd': 1.3458, 'e': -1.6264, 'f': 20.1315, 'g': None, 'h': None, 'i': None}],
    'WH': ['CZA', {'a': 0.59, 'b': 0.06, 'c': -2.0993, 'd': 0.8635, 'e': -1.026, 'f': 91.5562, 'g': None, 'h': None, 'i': None}],
    'RA': ['KOZ69', {'a': 0.97576, 'b': -1.22922, 'c': 0.25347, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'BM': ['KOZ69', {'a': 0.95997, 'b': -1.46336, 'c': 0.50339, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'SS': ['KOZ69', {'a': 0.99496, 'b': -1.98993, 'c': 0.99496, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'ES': ['KOZ69', {'a': 0.97449, 'b': -1.42305, 'c': 0.44856, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'AS': ['KOZ69', {'a': 0.95806, 'b': -1.33682, 'c': 0.37877, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'WP': ['KOZ69', {'a': 0.96272, 'b': -1.37551, 'c': 0.41279, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None}],
    'RC': ['KOZ88',
           {'a': 1.21697, 'b': 0.84256, 'c': 1.00001, 'd': 0.3, 'e': 1.55322, 'f': -0.39719, 'g': 2.11018, 'h': -1.11416, 'i': 0.0942}],
    'CW': ['KOZ88',
           {'a': 0.85258, 'b': 0.95297, 'c': 1.00048, 'd': 0.25, 'e': 0.73191, 'f': -0.08419, 'g': 0.19634, 'h': -0.06985, 'i': 0.14828}],
    'JP': ['WEN', {'a': 0.82932, 'b': 1.50831, 'c': -4.08016, 'd': 0.047053, 'e': 0.0, 'f': None, 'g': None, 'h': None, 'i': None}],
    'SP': ['WEN', {'a': 0.90051, 'b': 0.91588, 'c': -0.92964, 'd': 0.0077119, 'e': -0.0011019, 'f': None, 'g': None, 'h': None, 'i': None}],
    'WF': ['WEN', {'a': 0.86039, 'b': 1.45196, 'c': -2.42273, 'd': -0.15848, 'e': 0.036947, 'f': None, 'g': None, 'h': None, 'i': None}],
    'RF': ['WEN', {'a': 0.87927, 'b': 0.9135, 'c': -0.56617, 'd': -0.01448, 'e': 0.0037262, 'f': None, 'g': None, 'h': None, 'i': None}],
    'RW': ['WEN', {'a': 0.955, 'b': 0.387, 'c': -0.362, 'd': -0.00581, 'e': 0.00122, 'f': None, 'g': None, 'h': None, 'i': None}],
    'IC': ['WEN', {'a': 1.0, 'b': 0.3155, 'c': -0.34316, 'd': 0.0, 'e': -0.00039283, 'f': None, 'g': None, 'h': None, 'i': None}]}

#### SCRIBNER LOG LENGTH COEEFICIENTS AND FUNCTION
# KEY: VALUE -> {DIB: SCRIB COEFFICIENT}
SCRIBNER_DICT = {0: 0.0, 1: 0.0, 2: 0.143, 3: 0.39, 4: 0.676, 5: 1.07, 6: [1.16, 1.249, 1.57], 7: [1.4, 1.608, 1.8],
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
                 120: 695.011}


LOG_LENGTHS = {'<= 10 feet': (1, 10),
               '11 - 20 feet': (11, 20),
               '21 - 30 feet': (21, 30),
               '31 - 40 feet': (31, 40),
               '> 40 feet': (41, 999)}

SORTED_HEADS = [['tpa', 'TPA'], ['ba_ac', 'BASAL AREA'], ['rd_ac', 'RD'], ['qmd', 'QMD'], ['vbar', 'VBAR'],
                ['avg_hgt', 'AVG HEIGHT'], ['hdr', 'HDR'], ['bf_ac', 'BOARD FEET'], ['cf_ac', 'CUBIC FEET']]

OUTPUT_STAND_TABLE_HEADS = ('Stand', 'Plot Number', 'Tree Number', 'Species', 'DBH', 'Height',
                            'Stump Height', 'Log 1 Length', 'Log 1 Grade', 'Log 1 Defect', 'Between Logs Feet')

#FVS

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


# USEFUL FUNCTIONS


def format_comma(val: float):
    if val == 0:
        return '-'
    else:
        show = [i for i in str(round(val, 1))]
        if len(show) > 5:
            start = -5
            for i in range((len(show) // 3) - 1):
                show.insert(start, ',')
                start -= 4
        return ''.join(show)


def sort_grade(item):
    return GRADE_SORT[item[0]]


def extension_check(filename, extension):
    check = ''.join(filename[-len(extension):])
    if check != extension:
        filename += extension
    return filename


def get_filename_only(file_path):
    for i in range(-1, -len(file_path), -1):
        if file_path[i] == '/':
            return ''.join(file_path[i+1:])


def add_logs_to_table_heads(max_logs):
    master = []
    for i in range(2, max_logs + 1):
        for name in ['Length', 'Grade', 'Defect']:
            master.append(f'Log {i} {name}')
        if i < max_logs:
            master.append('Between Logs Feet')
    return master




