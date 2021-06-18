from openpyxl import Workbook
from csv import writer
from os.path import join, isfile, expanduser

METRICS_QUICK = ['Stand', 'Plot Number', 'Tree Number', 'Species', 'DBH', 'Height', 'Preferred Log Length', 'Min Log Length']
METRICS_FULL = ['Stand', 'Plot Number', 'Tree Number', 'Species', 'DBH', 'Height', 'Stump Height',
                'Log 1 Length', 'Log 1 Grade', 'Log 1 Defect %', 'Between Logs Feet',
                'Log 2 Length', 'Log 2 Grade', 'Log 2 Defect %', 'Between Logs Feet',
                'Log 3 Length', 'Log 3 Grade', 'Log 3 Defect %', 'Between Logs Feet',
                'Log 4 Length', 'Log 4 Grade', 'Log 4 Defect %', 'Between Logs Feet',
                'Log 5 Length', 'Log 5 Grade', 'Log 5 Defect %', 'Between Logs Feet',
                'Log 6 Length', 'Log 6 Grade', 'Log 6 Defect %', 'Between Logs Feet',
                'Log 7 Length', 'Log 7 Grade', 'Log 7 Defect %', 'Between Logs Feet',
                'Log 8 Length', 'Log 8 Grade', 'Log 8 Defect %']

DEFAULT_NAME_QUICK = 'stand_data_quick'
DEFAULT_NAME_FULL = 'stand_data_full'

def getdesktoppath():
    return join(expanduser("~"), "desktop")


def create_blank_csv(directory: str = None, full_cruise=False):
    if full_cruise:
        use_name = DEFAULT_NAME_FULL
    else:
        use_name = DEFAULT_NAME_QUICK

    if not directory:
        dir_ = getdesktoppath()
        title = join(dir_, use_name + '.csv')
    else:
        dir_ = directory
        title = join(dir_, use_name + '.csv')

    if isfile(title):
        is_file = True
        count = 1
        while is_file:
            title = join(dir_, use_name + f'_{count}.csv')
            if not isfile(title):
                is_file = False
            else:
                count += 1

    with open(title, 'w', newline='') as csv_file:
        row_write = writer(csv_file)
        if full_cruise:
            row_write.writerow(METRICS_FULL)
        else:
            row_write.writerow(METRICS_QUICK)
    return title



def create_blank_excel(directory: str = None, full_cruise=False):
    if full_cruise:
        use_name = DEFAULT_NAME_FULL
    else:
        use_name = DEFAULT_NAME_QUICK

    if not directory:
        dir_ = getdesktoppath()
        title = join(dir_, use_name + '.xlsx')
    else:
        dir_ = directory
        title = join(dir_, use_name + '.xlsx')

    if isfile(title):
        is_file = True
        count = 1
        while is_file:
            title = join(dir_, use_name + f'_{count}.xlsx')
            if not isfile(title):
                is_file = False
            else:
                count += 1

    wb = Workbook()
    ws = wb.active

    if full_cruise:
        use_metrics = METRICS_FULL
    else:
        use_metrics = METRICS_QUICK

    for i, met in enumerate(use_metrics):
        ws.cell(1, i + 1, met)

    wb.save(title)
    return title


if __name__ == '__main__':
    err = True
    q = None
    while err:
        q = input('\nWould you like a formatted CSV or Excel file (c / e)?: ').upper()
        if q == 'C' or q == 'E':
            err = False
        else:
            print('\nPlease enter either "c" or "e"')

    if q == 'C':
        file_type = 'CSV'
    else:
        file_type = 'Excel'

    err1 = True
    q1 = None
    full = False
    while err1:
        q1 = input('\nWould you like Full Cruise or Quick Cruise sheet (f / q)?: ').upper()
        if q1 == 'F' or q1 == 'Q':
            if q1 == 'F':
                full = True
            err1 = False
        else:
            print('\nPlease enter either "f" or "q"')

    q2 = input(f'\nWould you like to specify a directory?\nElse {file_type} file will be created on desktop\n(y / n): ').upper()
    if q2.upper() == 'Y':
        dir_ = input('\nDirectory path: ')
    else:
        dir_ = None

    try:
        if q == 'E':
            title = create_blank_excel(directory=dir_, full_cruise=full)
        else:
            title = create_blank_csv(directory=dir_, full_cruise=full)

        print(f'\n** Completed {file_type} file creation: "{title}" **')
    except FileNotFoundError:
        print(f'\n-- Original Directory "{dir_}" could not be found, {file_type} file will be created on Desktop --')

        if q == 'E':
            title = create_blank_excel(directory=None, full_cruise=full)
        else:
            title = create_blank_csv(directory=None, full_cruise=full)


        print(f'\n** Completed {file_type} file creation: "{title}" **')



