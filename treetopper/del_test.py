from treetopper.stand import Stand
from treetopper.fvs import FVS

stand = Stand('EX1', -25)
stand.import_sheet_quick('example_csv_and_xlsx/Example_CSV_quick.csv')
stand.console_report()

fvs = FVS()
fvs.set_stand(stand, 'PN', 612, 6, 45, 'DF', 120)
fvs.sqlite_db('testWIN3')