from os import getcwd
from os.path import (isfile,
                     join)
from copy import deepcopy
from datetime import date
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
from win32com.client import Dispatch
from pyodbc import connect as pycon
from sqlite3 import connect as sqcon
from _constants import (ACCESS_GROUPS_COLS,
                        ACCESS_STAND_COLS,
                        ACCESS_TREE_COLS,
                        SQL_GROUPS_COLS,
                        SQL_STAND_COLS,
                        SQL_TREE_COLS,
                        GROUPS_DEFAULTS,
                        get_filename_only,
                        extension_check)
from stand import Stand

class FVS(object):
    def __init__(self):
        self.stand = None
        self.stand_fvs = None
        self.tree_fvs = None

    def set_stand(self, stand, variant: str, forest_code: int, region: int, stand_age: int, site_species: str, site_index: int, **kwargs):
        self.stand = deepcopy(stand)
        self.stand_fvs = {i[0]: None for i in ACCESS_STAND_COLS[1]}
        self.tree_fvs = {}

        if self.stand.inv_date:
            inv_year = self.stand.inv_date.year
        else:
            inv_year = date.today().year

        self.stand_fvs['Stand_ID'] = self.stand.name
        self.stand_fvs['Variant'] = variant
        self.stand_fvs['Inv_Year'] = inv_year
        self.stand_fvs['Groups'] = 'All_Stands'
        self.stand_fvs['Region'] = region
        self.stand_fvs['Forest'] = forest_code
        self.stand_fvs['Age'] = stand_age
        self.stand_fvs['Basal_Area_Factor'] = self.stand.plot_factor
        self.stand_fvs['Brk_DBH'] = 0
        self.stand_fvs['Num_Plots'] = len(self.stand.plots)
        self.stand_fvs['Site_Species'] = site_species
        self.stand_fvs['Site_Index'] = site_index

        row = 1
        for i, plot in enumerate(self.stand.plots):
            pnum = i + 1
            std_plt = f'{self.stand.name}_{pnum}'
            for j, tree in enumerate(plot.trees):
                self.tree_fvs[row] = {i[0]: None for i in ACCESS_TREE_COLS[1]}
                self.tree_fvs[row]['Stand_ID'] = self.stand.name
                self.tree_fvs[row]['StandPlot_ID'] = std_plt
                self.tree_fvs[row]['Plot_ID'] = pnum
                self.tree_fvs[row]['Tree_ID'] = j + 1
                self.tree_fvs[row]['History'] = 1
                self.tree_fvs[row]['Species'] = tree.species
                self.tree_fvs[row]['DBH'] = tree.dbh
                self.tree_fvs[row]['Ht'] = tree.height
                row += 1

        for key in kwargs:
            if key in self.stand_fvs:
                self.stand_fvs[key] = kwargs[key]

    def access_db(self, filename: str, directory: str = None, blank_db: bool = False):
        db_save = extension_check(filename, '.accdb')
        db_short = get_filename_only(db_save)

        if directory:
            db_path = join(directory, db_save)
        else:
            db_path = join(getcwd(), db_save)

        db_exists = True

        if not isfile(db_path):
            self._create_access_db(db_path)
            db_exists = False

        drive = '{Microsoft Access Driver (*.mdb, *.accdb)}'
        connection_text = r'DRIVER={driver};DBQ={filename};'.format(driver=drive, filename=db_path)
        con = pycon(connection_text)
        cur = con.cursor()

        if not db_exists:
            sql = f"""INSERT INTO FVS_GroupAddFilesAndKeywords (Groups, FVSKeywords) VALUES (?, ?)"""
            cur.execute(sql, [GROUPS_DEFAULTS[0], GROUPS_DEFAULTS[1].format(DB_NAME=db_short)])
            con.commit()

        if not blank_db:
            self._insert_sql(con, cur)

        con.close()

    def sqlite_db(self, filename: str, directory: str = None, blank_db: bool = False):
        db_save = extension_check(filename, '.db')
        db_short = get_filename_only(db_save)

        if directory:
            db_path = join(directory, db_save)
        else:
            db_path = join(getcwd(), db_save)

        if not isfile(db_path):
            con, cur = self._create_sqlite_db(db_path, db_short)
        else:
            con = sqcon(db_path)
            cur = con.cursor()

        if not blank_db:
            self._insert_sql(con, cur)

        con.close()

    def excel_db(self, filename: str, directory: str = None, blank_db: bool = False):
        db_save = extension_check(filename, '.xlsx')
        db_short = get_filename_only(db_save)

        if directory:
            db_path = join(directory, db_save)
        else:
            db_path = join(getcwd(), db_save)

        if not isfile(db_path):
            wb = self._create_excel_db(db_short)
        else:
            wb = load_workbook(db_path)

        if not blank_db:
            self._insert_excel(wb)

        wb.save(db_path)

    def _create_access_db(self, db_path:  str):
        access = Dispatch("Access.Application")
        access_engine = access.DBEngine
        access_workspace = access_engine.Workspaces(0)
        access_language = ';LANGID=0x0409;CP=1252;COUNTRY=0'
        access_db = access_workspace.CreateDatabase(db_path, access_language, 64)

        for table in [ACCESS_GROUPS_COLS, ACCESS_STAND_COLS, ACCESS_TREE_COLS]:
            sql = f'CREATE TABLE {table[0]} (' + ', '.join([f'{i[0]} {i[1]}' for i in table[1]]) + ');'
            access_db.Execute(sql)

    def _create_sqlite_db(self, db_path: str, db_short: str):
        con = sqcon(db_path)
        cur = con.cursor()
        for i, table in enumerate([SQL_GROUPS_COLS, SQL_STAND_COLS, SQL_TREE_COLS]):
            sql = f'CREATE TABLE {table[0]} (' + ', '.join([f'{i[0]} {i[1]}' for i in table[1]]) + ');'
            cur.execute(sql)

        sql = f"""INSERT INTO FVS_GroupAddFilesAndKeywords (Groups, FVSKeywords) VALUES (?, ?)"""
        cur.execute(sql, [GROUPS_DEFAULTS[0], GROUPS_DEFAULTS[1].format(DB_NAME=db_short)])
        con.commit()
        return con, cur

    def _create_excel_db(self, db_short: str):
        wb = Workbook()
        for i, table in enumerate([ACCESS_GROUPS_COLS, ACCESS_STAND_COLS, ACCESS_TREE_COLS]):
            ws = wb.create_sheet(table[0])
            for j, col in enumerate(table[1]):
                ws.cell(1, j + 1).value = col[0]
            if i == 0:
                ws.cell(2, 1).value = GROUPS_DEFAULTS[0]
                ws.cell(2, 3).value = GROUPS_DEFAULTS[1].format(DB_NAME=db_short)
                ws.cell(2, 3).alignment = Alignment(wrapText=True)

        for sheet in wb.sheetnames:
            if sheet not in [ACCESS_GROUPS_COLS[0], ACCESS_STAND_COLS[0], ACCESS_TREE_COLS[0]]:
                wb.remove(wb[sheet])
        return wb

    def _insert_sql(self, connection, cursor):
        stand_cols = [col for col in self.stand_fvs if self.stand_fvs[col]]
        stand_vals = [self.stand_fvs[col] for col in self.stand_fvs if self.stand_fvs[col]]
        stand_sql = f"""INSERT INTO FVS_StandInit ({', '.join(stand_cols)}) VALUES ({', '.join(['?' for _ in stand_cols])})"""
        cursor.execute(stand_sql, stand_vals)

        for row in self.tree_fvs:
            tree_cols = [col for col in self.tree_fvs[row] if self.tree_fvs[row][col]]
            tree_vals = [self.tree_fvs[row][col] for col in self.tree_fvs[row] if self.tree_fvs[row][col]]
            tree_sql = f"""INSERT INTO FVS_TreeInit ({', '.join(tree_cols)}) VALUES ({', '.join(['?' for _ in tree_cols])})"""

            cursor.execute(tree_sql, tree_vals)
        connection.commit()

    def _insert_excel(self, workbook):
        stand_keys = list(self.stand_fvs)
        stand_cols = [col for col in self.stand_fvs if self.stand_fvs[col]]
        stand_idxs = [stand_keys.index(col) + 1 for col in stand_cols]
        stand_vals = [self.stand_fvs[col] for col in self.stand_fvs if self.stand_fvs[col]]

        ws = workbook['FVS_StandInit']
        next_row = ws.max_row + 1
        for idx, val in zip(stand_idxs, stand_vals):
            ws.cell(next_row, idx).value = val

        ws = workbook['FVS_TreeInit']
        next_row = ws.max_row + 1
        tree_keys = list(self.tree_fvs[1])
        for row in self.tree_fvs:
            tree_cols = [col for col in self.tree_fvs[row] if self.tree_fvs[row][col]]
            tree_idxs = [tree_keys.index(col) + 1 for col in tree_cols]
            tree_vals = [self.tree_fvs[row][col] for col in self.tree_fvs[row] if self.tree_fvs[row][col]]
            for idx, val in zip(tree_idxs, tree_vals):
                ws.cell(next_row, idx).value = val
            next_row += 1







if __name__ == '__main__':
    stand = Stand('OK2', 46.94)
    stand.from_csv_full('Example_CSV_full.csv')
    fvs = FVS()
    fvs.set_stand(stand, 'PN', 612, 6, 50, 'DF', 120)
    fvs.excel_db('spam')

