from openpyxl import load_workbook

blank = 'C:/FVS/Blank Databases/BlankDatabase.xlsx'
wb = load_workbook(blank)
ws = wb['FVS_TreeInit']

attrs = []
for line in ws.iter_rows(min_row=1, max_row=1):
    for l in line:
        attrs.append(l.value)
print(attrs)





class FVS(object):
    def __init__(self):
        pass