from datetime import date, datetime
from os.path import join, expanduser


def get_desktop_path():
    return join(expanduser("~"), "desktop")


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


def format_pct(val: float):
    if val <= 1:
        return f'{round(val * 100, 1)} %'
    else:
        return f'{round(val, 1)} %'


def extension_check(filename, extension):
    check = ''.join(filename[-len(extension):])
    if check != extension:
        filename += extension
    return filename


def get_extension(filename):
    rev_file_list = [i for i in reversed(list(filename))]
    ext = []
    for i in rev_file_list:
        if i == '.':
            ext.append(i)
            break
        else:
            ext.append(i)
    return ''.join([i for i in reversed(ext)])


def get_filename_only(file_path):
    for i in range(-1, -len(file_path), -1):
        if file_path[i] == '/':
            return ''.join(file_path[i+1:])


def reorder_dict(unordered):
    reorder = {}
    unordered_list = list(unordered)
    unordered_list.append(unordered_list.pop(0))
    for i in unordered_list:
        reorder[i] = unordered[i]
    return reorder


def check_date(value):
    """Checks the value of the inventory_date class-argument and returns a date object"""
    delimiters = [',', '.', '/', '-', '_', ':', ';', '?', '|', '~', '`']
    if isinstance(value, str):
        try:
            month, day, year = value[:2], value[2:4], value[4:]
            if len(year) < 4:
                year = f'20{year}'
            month, day, year = int(month), int(day), int(year)
            return date(year, month, day)
        except ValueError:
            for i in delimiters:
                try:
                    month, day, year = value.split(i)
                    if len(year) < 4:
                        year = f'20{year}'
                    month, day, year = int(month), int(day), int(year)
                    return date(year, month, day)
                except:
                    next
            else:
                raise Exception('Invalid date separator -- try */* as in MM/DD/YYYY')
    elif isinstance(value, datetime):
        return date(value.year, value.month, value.day)
    elif isinstance(value, date):
        return value
    else:
        raise Exception('Invalid date')


def add_logs_to_table_heads(max_logs):
    """Adds log headers to table data depending on the maximum number of logs from trees within the stand"""
    master = []
    for i in range(2, max_logs + 1):
        for name in ['Length', 'Grade', 'Defect']:
            master.append(f'Log {i} {name}')
        if i < max_logs:
            master.append('Between Logs Feet')
    return master


def is_err_num(val, row_num, col_num, num_type, required=True, default=None):
    if val == '' or val is None:
        if required:
            if default is None:
                return True, val, f'Row {row_num + 1}, Col {col_num + 1} Cannot be blank'
            else:
                return False, default, None
        else:
            return False, default, None
    else:
        try:
            x = num_type(val)
            if x < 0:
                return True, val,  f'Row {row_num + 1}, Col {col_num + 1} Value: ({val}) cannot be negative'
            else:
                return False, x, None
        except ValueError:
            return True, val, f'Row {row_num + 1}, Col {col_num + 1} Value: ({val}) has to be a number'


