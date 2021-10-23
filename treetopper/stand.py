from os import (startfile,
                getcwd)
from os.path import (join,
                     isfile)
from csv import (writer,
                 excel)
from openpyxl import (Workbook,
                      load_workbook)
from datetime import (datetime,
                      date)
from statistics import (mean,
                        variance,
                        stdev)
from treetopper.plot import Plot
from treetopper.timber import (TimberQuick,
                               TimberFull)
from treetopper.log import Log
from treetopper.thin import (
    ThinTPA,
    ThinBA,
    ThinRD,
    TargetDensityError
)
from treetopper.fvs import FVS
from treetopper._constants import (math,
                                   extension_check,
                                   LOG_LENGTHS)
from treetopper._import_from_sheets import (import_csv_quick,
                                            import_csv_full,
                                            import_excel_quick,
                                            import_excel_full)
from treetopper._console_print import (print_species,
                                       print_logs,
                                       print_species_stats)
from treetopper._pdf_print import PDF



class Stand(object):
    """The Stand Class represents a stand of timber that has had an inventory conducted on it. It should made up of plots (Plot Class)
       which contain trees (Timber Classes).

       The Stand class will run calculations and statistics of the current stand conditions and it will run calculations of the log
       merchantabilty for three metrics: logs per acre, log board feet per acre, and log cubic feet per acre, based on log grades,
       log length ranges and species.

       Tree and Plot data can be entered manually into the Stand Class. The manual entry work flow should look like...

       If using the quick cruise functionality of the TimberQuick class, the flow should be:

        instantiate Stand -->

        instantiate Trees (w/ TimberQuick) -->

        create a list of lists based on number of plots, the sub-lists will contain the trees -->

        iterate through the trees list and instantiate a plot at the beginning of the iteration -->

        iterate through the sub list and add the trees to the plot using plot.add_tree(tree) -->

        after the trees have been added from the sub list, add the plot to the Stand using stand.add_plot(plot)

       If using the full cruise functionality of the TimberFull class, the flow should be:

        instantiate Stand -->

        instantiate Trees (w/ TimberFull) -->

        create a list of lists based on number of plots, the sub-lists will contain the trees and log arguments -->

        iterate through the trees/logs list and instantiate a plot at the beginning of the iteration -->

        iterate through the sub list and then iterate though the logs metric sub list and add the logs to the tree
        using tree.add_log(stem_height, length, grade, defect) -->

        after the logs have been added, add the tree to the plot using plot.add_tree(tree) -->

        after the trees have been added from the sub list, add the plot to the Stand using stand.add_plot(plot)

       Plots and Trees can also be read from CSV and Excel files

       ** these files need to be formatted correctly **

       To create a formatted blank CSV or Excel file, open the terminal and type "python -m treetopper.blank_sheet" and
       run through the prompts

       Once data has been added to the sheet, instantiate a Stand and call either:

        stand.from_csv_quick(file_path)

        stand.from_csv_full(file_path)

        stand.from_excel_quick(file_path) OR

        stand.from_excel_full(file_path)

       depending on the file type you are using and the cruise method of the stand.

       Once Plots and Trees have been added, two types of reports can be generated: a PDF report or a simple console report, these
       reports will display the current stand conditions by species and total; the log merchantability by grade, log length range,
       and species in three categories: logs per acre, board feet per acre and cubic feet per acre; and the stand condition statistics
       by species and total. To generate these reports call:

        stand.pdf_report() OR

        stand.console_report()

       Stands can also be thinned using the Thinning Classes, the three thinning classes are ThinTPA, ThinBA, and ThinRD, they will thin
       the stand based on a target Trees per Acre, Basal Area per Acre or Relative Density per Acre, respectively. The user can also
       choose certain species to cut, and minimum and maximum diameter limits.

       See __name__ == '__main__' for example workflows.

       HAPPY CRUISING!


       """

    def __init__(self, name:str, plot_factor: float, acres:float = None, inventory_date:str = None):
        self.name = name
        self.plot_factor = plot_factor
        self.plots = []
        self.plot_count = 0

        self.tpa = 0
        self.ba_ac = 0
        self.qmd = 0
        self.rd_ac = 0
        self.bf_ac = 0
        self.cf_ac = 0
        self.avg_hgt = 0
        self.hdr = 0
        self.vbar = 0

        self.tpa_stats = {}
        self.ba_ac_stats = {}
        self.rd_ac_stats = {}
        self.bf_ac_stats = {}
        self.cf_ac_stats = {}

        self.species = {}
        self.species_gross = {}
        self.species_stats = {}

        self.logs = {}

        self.table_data = []

        self.metrics = ['tpa', 'ba_ac', 'rd_ac', 'bf_ac', 'cf_ac']
        self.attrs = ['_gross', '_stats', '']

        self.acres = acres
        if inventory_date:
            self.inv_date = self._check_date(inventory_date)
        else:
            self.inv_date = inventory_date

    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]

    def console_report(self):
        """Returns a console-formatted string of the processed stand data, to be called by the standard print() function"""
        console_text = '\nSTAND METRICS'
        console_text += f'\n{print_species(self.species)}'
        console_text += '\n\nLOG METRICS'
        console_text += f'\n{print_logs(self.logs)}'
        console_text += '\nSTAND STATISTICS'
        console_text += f'{print_species_stats(self.species_stats)}'
        # print(console_text)
        return console_text

    def pdf_report(self, filename: str, directory: str = None):
        """Exports a pdf of the stand report to a user specified directory or if directory is None, to the current working directory"""
        check = extension_check(filename, '.pdf')
        if directory:
            file = join(directory, check)
        else:
            file = join(getcwd(), check)
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.compile_report(self)
        pdf.output(file, 'F')
        startfile(file)

    #@timer
    def add_plot(self, plot: Plot):
        """Adds a plot to the stand's plots list and re-runs the calculations and statistics of the stand.
           plot argument needs to be the a Plot Class"""
        self.plots.append(plot)
        self.plot_count += 1
        for met in self.metrics:
            self._update_metrics(met)
        self.qmd = math.sqrt((self.ba_ac / self.tpa) / .005454)
        self.vbar = self.bf_ac / self.ba_ac
        self._update_species(plot)
        self._update_logs(plot)
        self.table_data = self._update_table_data()

    def from_csv_quick(self, file_path):
        """Imports tree and plot data from a CSV file for a quick cruise and adds that data to the stand"""
        plots, avg_hdr = import_csv_quick(file_path, self.name)
        for pnum in plots:
            plot = Plot()
            for tree in plots[pnum]:
                mets = plots[pnum][tree]
                if mets['height'] == '':
                    height = int((mets['dbh'] / 12) * avg_hdr)
                else:
                    height = mets['height']
                plot.add_tree(TimberQuick(mets['species'], mets['dbh'], height, self.plot_factor,
                                          preferred_log_length=mets['pref_log'], minimum_log_length=mets['min_log']))
            self.add_plot(plot)

    def from_csv_full(self, file_path):
        """Imports tree and plot data from a CSV file for a full cruise and adds that data to the stand"""
        plots, avg_hdr = import_csv_full(file_path, self.name)
        for pnum in plots:
            plot = Plot()
            for tnum in plots[pnum]:
                mets = plots[pnum][tnum]
                if not mets['height']:
                    height = int((mets['dbh'] / 12) * avg_hdr)
                else:
                    height = mets['height']
                tree = TimberFull(mets['species'], mets['dbh'], height, self.plot_factor)
                for lnum in mets['logs']:
                    tree.add_log(*mets['logs'][lnum])
                plot.add_tree(tree)
            self.add_plot(plot)

    def from_excel_quick(self, file_path):
        """Imports tree and plot data from an Excel file for a quick cruise and adds that data to the stand"""
        plots, avg_hdr = import_excel_quick(file_path, self.name)
        for pnum in plots:
            plot = Plot()
            for tree in plots[pnum]:
                mets = plots[pnum][tree]
                if not mets['height']:
                    height = int((mets['dbh'] / 12) * avg_hdr)
                else:
                    height = mets['height']
                plot.add_tree(TimberQuick(mets['species'], mets['dbh'], height, self.plot_factor,
                                          preferred_log_length=mets['pref_log'], minimum_log_length=mets['min_log']))
            self.add_plot(plot)

    def from_excel_full(self, file_path):
        """Imports tree and plot data from an Excel file for a full cruise and adds that data to the stand"""
        plots, avg_hdr = import_excel_full(file_path, self.name)
        for pnum in plots:
            plot = Plot()
            for tnum in plots[pnum]:
                mets = plots[pnum][tnum]
                if not mets['height']:
                    height = int((mets['dbh'] / 12) * avg_hdr)
                else:
                    height = mets['height']
                tree = TimberFull(mets['species'], mets['dbh'], height, self.plot_factor)
                for lnum in mets['logs']:
                    tree.add_log(*mets['logs'][lnum])
                plot.add_tree(tree)
            self.add_plot(plot)

    def table_to_csv(self, filename: str, directory: str = None):
        """Creates or appends a CSV file with tree data from self.table_data"""
        check = extension_check(filename, '.csv')
        if directory:
            file = join(directory, check)
        else:
            file = join(getcwd(), check)

        if isfile(file):
            allow = 'a'
            start = 1
        else:
            allow = 'w'
            start = 0

        with open(file, allow, newline='') as csv_file:
            csv_write = writer(csv_file, dialect=excel)
            for i in self.table_data[start:]:
                csv_write.writerow(i)

    def table_to_excel(self, filename: str, directory: str = None):
        """Creates or appends an Excel file with tree data from self.table_data"""
        check = extension_check(filename, '.xlsx')
        if directory:
            file = join(directory, check)
        else:
            file = join(getcwd(), check)

        if isfile(file):
            wb = load_workbook(file)
            ws = wb.active
            for i in self.table_data[1:]:
                ws.append(i)
            wb.save(file)
        else:
            wb = Workbook()
            ws = wb.active
            for i in self.table_data:
                ws.append(i)
            wb.save(file)

    def _update_table_data(self):
        heads = ['Stand', 'Plot Number', 'Tree Number', 'Species', 'DBH', 'Height',
                 'Stump Height', 'Log 1 Length', 'Log 1 Grade', 'Log 1 Defect', 'Between Logs Feet']
        master = []
        max_logs = []
        for i, plot in enumerate(self.plots):
            for j, tree in enumerate(plot.trees):
                temp = [self.name, i + 1, j + 1]
                for key in ['species', 'dbh', 'height']:
                    temp.append(tree[key])
                len_logs = len(tree.logs)
                max_logs.append(len_logs)
                for k, lnum in enumerate(tree.logs):
                    log = tree.logs[lnum]
                    if lnum == 1:
                        temp.append(log.stem_height - log.length - 1)
                    for lkey in ['length', 'grade', 'defect']:
                        temp.append(log[lkey])
                    if k < len(tree.logs) - 1:
                        between = tree.logs[lnum+1].stem_height - log.stem_height - tree.logs[lnum+1].length - 1
                        if between < 0:
                            temp.append(0)
                        else:
                            temp.append(between)
                master.append(temp)

        heads += self._add_logs_to_table_heads(max(max_logs))
        len_heads = len(heads)
        for i in master:
            len_i = len(i)
            if len_i < len_heads:
                i += ['' for j in range(len_heads - len_i)]
        master.insert(0, heads)
        return master

    def _update_metrics(self, metric: str):
        """Updates stand metrics based on the metric entered in the argument, used internally"""
        metric_list = [plot[metric] for plot in self.plots]
        stats = self._get_stats(metric_list)
        setattr(self, metric, stats['mean'])
        setattr(self, f'{metric}_stats', stats)

    def _update_species(self, plot):
        """Re-runs stand conditions calculations and statistics"""
        update_after = ['qmd', 'vbar', 'avg_hgt', 'hdr']
        if self.plot_count == 0:
            return
        else:
            for species in plot.species:
                if species not in self.species_gross:
                    for attr in self.attrs:
                        if attr == '_gross':
                            getattr(self, f'species{attr}')[species] = {met: [] for met in self.metrics}
                        else:
                            getattr(self, f'species{attr}')[species] = {met: 0 for met in self.metrics}
                for key in plot.species[species]:
                    if key not in update_after:
                        self.species_gross[species][key].append(plot.species[species][key])
            for species in self.species_gross:
                for key in self.species_gross[species]:
                    if key not in update_after:
                        data = self.species_gross[species][key]
                        if len(data) < self.plot_count:
                            data += ([0] * (self.plot_count - len(data)))
                        stats = self._get_stats(data)
                        self.species[species][key] = stats['mean']
                        self.species_stats[species][key] = stats
                self.species[species]['qmd'] = math.sqrt((self.species[species]['ba_ac'] / self.species[species]['tpa']) / 0.005454)
                self.species[species]['vbar'] = self.species[species]['bf_ac'] / self.species[species]['ba_ac']
                if species == 'totals_all':
                    self.species[species]['avg_hgt'] = mean([p.avg_hgt for p in self.plots])
                    self.species[species]['hdr'] = mean([p.hdr for p in self.plots])
                else:
                    trees = []
                    for p in self.plots:
                        for t in p.trees:
                            trees.append(t)
                    self.species[species]['avg_hgt'] = mean([t.height for t in trees if t.species == species])
                    self.species[species]['hdr'] = mean([t.hdr for t in trees if t.species == species])

    def _update_logs(self, plot):
        """Re-runs stand logs calculations"""
        if self.plot_count == 0:
            return
        else:
            subs = ['lpa', 'bf_ac', 'cf_ac']
            for species in plot.logs:
                if species not in self.logs:
                    self.logs[species] = {}
                for grade in plot.logs[species]:
                    if grade not in self.logs[species]:
                        self.logs[species][grade] = {rng: {sub: {'gross': [], 'mean': 0} for sub in subs} for rng in LOG_LENGTHS}
                        self.logs[species][grade]['totals_by_grade'] = {sub: {'gross': [], 'mean': 0} for sub in subs}
                    for rng in plot.logs[species][grade]:
                        if rng != 'display':
                            for sub in subs:
                                self.logs[species][grade][rng][sub]['gross'].append(plot.logs[species][grade][rng][sub])
            for species in self.logs:
                for grade in self.logs[species]:
                    for rng in self.logs[species][grade]:
                        for sub in subs:
                            gross = self.logs[species][grade][rng][sub]['gross']
                            if len(gross) < self.plot_count:
                                gross += ([0] * (self.plot_count - len(gross)))
                            self.logs[species][grade][rng][sub]['mean'] = mean(gross)


    def _check_date(self, value):
        """Checks the value of the inventory_date class-argument and returns a date object"""
        delimiters = [',', '.', '/', '-', '_', ':', ';', '?', '|', '~', '`']
        if isinstance(value, str):
            try:
                month, day, year = value[:2], value[2:4], value[4:]
                if len(year) < 4:
                    year = f'20{year}'
                month, day, year = int(month), int(day), int(year)
                return date(year, month, day)
            except:
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

    def _add_logs_to_table_heads(self, max_logs):
        """Adds log headers to table data depending on the maximum number of logs from trees within the stand"""
        master = []
        for i in range(2, max_logs + 1):
            for name in ['Length', 'Grade', 'Defect']:
                master.append(f'Log {i} {name}')
            if i < max_logs:
                master.append('Between Logs Feet')
        return master

    def _get_stats(self, data):
        """Runs the statistical calculations on a set of the stand conditions data, returns an updated sub dict"""
        m = mean(data)
        if len(data) >= 2:
            std = stdev(data)
            ste = std / math.sqrt(self.plot_count)
            low_avg_high = [max(round(m - ste, 1), 0), m, m + ste]
            d = {'mean': m,
                 'variance': variance(data),
                 'stdev': std,
                 'stderr': ste,
                 'stderr_pct': (ste / m) * 100,
                 'low_avg_high': low_avg_high}
        else:
            d = {'mean': m,
                 'variance': 'Not enough data',
                 'stdev': 'Not enough data',
                 'stderr': 'Not enough data',
                 'stderr_pct': 'Not enough data',
                 'low_avg_high': 'Not enough data'}
        return d


if __name__ == '__main__':
    import argparse
    import traceback
    import sys
    from os import mkdir, getcwd
    from os.path import join, isfile, isdir, expanduser

    def get_desktop_path():
        return join(expanduser("~"), "desktop")

    def make_dir_and_subdir(workflow_num):
        desktop = get_desktop_path()

        tt_dir = join(desktop, 'treetopper_outputs')
        if not isdir(tt_dir):
            mkdir(tt_dir)

        wf_dir = join(tt_dir, f'workflow_{workflow_num}')
        if not isdir(wf_dir):
            mkdir(wf_dir)

        return wf_dir

    def get_package_path(filename):
        path = None
        for i in sys.path:
            if 'AppData' in i and i[-13:] == 'site-packages':
                path = i
                break
        tt_path = join(path, 'treetopper')
        final = join(tt_path, filename)
        print(final)
        return final



    parser = argparse.ArgumentParser(description='treetopper Example Workflows')
    parser.add_argument('workflow_number', help='Enter the number of the workflow to run.\n Valid workflow numbers: 1, 2, 3, 4, 5, 6)')
    args = parser.parse_args()

    wf = args.workflow_number
    while True:
        if wf not in ['1', '2', '3', '4', '5', '6']:
            print('Please enter a workflow number 1, 2, 3, 4, 5, or 6')
            wf = input('Workflow #: ')
        else:
            break
    wf = int(wf)


    def workflow_1(workflow_number):
        stand = Stand('WF1', -20)
        plot_factor = stand.plot_factor
        tree_data = [[TimberQuick('DF', 29.5, 119, plot_factor), TimberQuick('WH', 18.9, 102, plot_factor),
                      TimberQuick('WH', 20.2, 101, plot_factor), TimberQuick('WH', 19.9, 100, plot_factor),
                      TimberQuick('DF', 20.6, 112, plot_factor)],
                     [TimberQuick('DF', 25.0, 117, plot_factor), TimberQuick('DF', 14.3, 105, plot_factor),
                      TimberQuick('DF', 20.4, 119, plot_factor), TimberQuick('DF', 16.0, 108, plot_factor),
                      TimberQuick('RC', 20.2, 124, plot_factor), TimberQuick('RC', 19.5, 116, plot_factor),
                      TimberQuick('RC', 23.4, 121, plot_factor), TimberQuick('DF', 17.8, 116, plot_factor),
                      TimberQuick('DF', 22.3, 125, plot_factor)]
                     ]
        for trees in tree_data:
            plot = Plot()
            for tree in trees:
                plot.add_tree(tree)
            stand.add_plot(plot)

        path = make_dir_and_subdir(workflow_number)

        print(stand.console_report())
        stand.table_to_csv(join(path, 'example_csv_export.csv'))

        thin80tpa = ThinTPA(stand, 80)
        print(thin80tpa.console_report())

        end_message = """**WORKFLOW 1 created a QUICK CRUISE stand from manually entered tree data.

  It then ran a thinning scenario with a target density of 80 Trees per Acre considering all species and diameter ranges.

  Outputs:
      Stand console report in terminal [print(stand_class.console_report)] ^above^
      Thinning console report in terminal [print(thin_class.console_report))] ^above^
      Plot data .csv "example_csv_export.csv" in desktop/treetopper_outputs/workflow_1/
"""
        print(f'\n\n{end_message}')


    def workflow_2(workflow_number):
        stand = Stand('WF2', 33.3)
        plot_factor = stand.plot_factor
        tree_data = [[[TimberFull('DF', 29.5, 119, plot_factor), [[42, 40, 'S2', 5], [83, 40, 'S3', 0], [102, 18, 'S4', 10]]],
                      [TimberFull('WH', 18.9, 102, plot_factor), [[42, 40, 'S2', 0], [79, 36, 'S4', 5]]],
                      [TimberFull('WH', 20.2, 101, plot_factor), [[42, 40, 'S2', 5], [83, 40, 'S4', 0]]],
                      [TimberFull('WH', 19.9, 100, plot_factor), [[42, 40, 'S2', 0], [83, 40, 'S4', 15]]],
                      [TimberFull('DF', 20.6, 112, plot_factor), [[42, 40, 'S2', 0], [83, 40, 'S3', 5], [100, 16, 'UT', 10]]]],
                     [[TimberFull('DF', 25.0, 117, plot_factor), [[42, 40, 'SM', 0], [83, 40, 'S3', 5], [100, 16, 'S4', 0]]],
                      [TimberFull('DF', 14.3, 105, plot_factor), [[42, 40, 'S3', 0], [79, 36, 'S4', 0]]],
                      [TimberFull('DF', 20.4, 119, plot_factor), [[42, 40, 'S2', 5], [83, 40, 'S3', 5], [100, 16, 'S4', 5]]],
                      [TimberFull('DF', 16.0, 108, plot_factor), [[42, 40, 'S3', 5], [83, 40, 'S3', 10]]],
                      [TimberFull('RC', 20.2, 124, plot_factor), [[42, 40, 'CR', 5], [83, 40, 'CR', 5], [104, 20, 'CR', 5]]],
                      [TimberFull('RC', 19.5, 116, plot_factor), [[42, 40, 'CR', 10], [83, 40, 'CR', 5], [100, 16, 'CR', 0]]],
                      [TimberFull('RC', 23.4, 121, plot_factor), [[42, 40, 'CR', 0], [83, 40, 'CR', 0], [106, 22, 'CR', 5]]],
                      [TimberFull('DF', 17.8, 116, plot_factor), [[42, 40, 'S2', 0], [83, 40, 'S3', 0], [100, 16, 'S4', 10]]],
                      [TimberFull('DF', 22.3, 125, plot_factor), [[42, 40, 'SM', 0], [83, 40, 'S3', 5], [108, 24, 'S4', 0]]]]
                     ]
        for trees in tree_data:
            plot = Plot()
            for tree in trees:
                for log in tree[1]:
                    tree[0].add_log(*log)
                plot.add_tree(tree[0])
            stand.add_plot(plot)

        path = make_dir_and_subdir(workflow_number)

        print(stand.console_report())
        stand.table_to_excel(join(path, 'example_xlsx_export.xlsx'))

        thin120ba = ThinBA(stand, 120, species_to_cut=['DF', 'WH'])
        print(thin120ba.console_report())

        end_message = """**WORKFLOW 2 created a FULL CRUISE stand from manually entered tree data.

  It then ran a thinning scenario with a target density of 120 Basal Area per Acre harvesting only DF and WH considering all diameter ranges.

  Outputs:
      Stand console report in terminal [print(stand_class.console_report)] ^above^
      Thinning console report in terminal [print(thin_class.console_report))] ^above^
      Plot data .xlsx "example_xlsx_export.xlsx" in desktop/treetopper_outputs/workflow_2/
"""
        print(f'\n\n{end_message}')


    def workflow_3(workflow_number):
        path = make_dir_and_subdir(workflow_number)

        stand = Stand('EX4', -30)
        stand.from_excel_quick(join(getcwd(), 'Example_Excel_quick.xlsx'))
        print(stand.console_report())

        stand.table_to_excel(join(path, 'example_xlsx_export.xlsx'))

        thin25rd = ThinRD(stand, 25, species_to_cut=['DF', 'WH'], min_dbh_to_cut=10, max_dbh_to_cut=18)
        print(thin25rd.console_report())

        end_message = """**WORKFLOW 3 created a QUICK CRUISE stand from importing plot data from an excel sheet.

  It then ran a thinning scenario with a target density of 25 Relative Density per Acre harvesting only DF and WH, with a
  minimum dbh of 10 inches and a maximum dbh of 18 inches. ** Note this thinning density won't be able to be achieved
  fully because our parameters don't allow for the needed harvest density, but this is to illustrate that the thinning
  will let the user know how much density was taken and how much more is needed to achieve the desired density target

  Outputs:
      Stand console report in terminal [print(stand_class.console_report)] ^above^
      Thinning console report in terminal [print(thin_class.console_report))] ^above^
      Plot data .xlsx "example_xlsx_export.xlsx" in desktop/treetopper_outputs/workflow_3/
"""
        print(f'\n\n{end_message}')


    def workflow_4(workflow_number):
        path = make_dir_and_subdir(workflow_number)

        stand = Stand('OK2', 46.94)
        stand.from_csv_full(get_package_path('Example_CSV_full.csv'))
        print(stand.console_report())
        stand.table_to_excel(join(path, 'example_xlsx_export.xlsx'))

        try:
            thin100tpa = ThinTPA(stand, 100)
            print(thin100tpa.console_report())
        except TargetDensityError as e:
            print(traceback.format_exc())

        end_message = """**WORKFLOW 4 created a FULL CRUISE stand from importing plot data from an csv sheet.

  It then ran a thinning scenario with a target density of 100 Trees per Acre considering all species and diameter ranges.
  ** Note this thinning density is greater than the current stand density and the Thin Class will throw a TargetDensityError exception
  which will explain what went wrong.

  Outputs:
      Stand console report in terminal [print(stand_class.console_report)] ^above^
      Thinning console report in terminal [print(thin_class.console_report))] ^above^
      Plot data .xlsx "example_xlsx_export.xlsx" in desktop/treetopper_outputs/workflow_4/
"""
        print(f'\n\n{end_message}')


    def workflow_5(workflow_number):
        path = make_dir_and_subdir(workflow_number)

        stand = Stand('EX3', 33.3)
        stand.from_csv_quick(get_package_path('Example_CSV_quick.csv'))
        stand.pdf_report(join(path, 'stand_report.pdf'))
        stand.table_to_excel(join(path, 'example_xlsx_export.xlsx'))

        thin140ba = ThinBA(stand, 140, species_to_cut=['DF', 'WH', 'RA'], max_dbh_to_cut=24)
        thin140ba.pdf_report(join(path, 'thin_report.pdf'))

        end_message = """**WORKFLOW 5 created a QUICK CRUISE stand from importing plot data from an csv sheet.

  It then ran a thinning scenario with a target density of 140 Basal Area per Acre harvesting only DF, WH and RA with a maximum diameter of 24 inches.

  Outputs:
      Stand PDF report "stand_report.pdf" from [stand_class.pdf_report()] in desktop/treetopper_outputs/workflow_5/
      Thinning PDF report "thin_report.pdf" from [thin_class.pdf_report()] in desktop/treetopper_outputs/workflow_5/
      Plot data .xlsx "example_xlsx_export.xlsx" in desktop/treetopper_outputs/workflow_5/
"""
        print(f'\n\n{end_message}')


    def workflow_6(workflow_number):
        path = make_dir_and_subdir(workflow_number)

        stand = Stand('OK1', -30)
        stand.from_excel_full(get_package_path('Example_Excel_full.xlsx'))
        stand.table_to_excel(join(path, 'example_xlsx_export.xlsx'))

        fvs = FVS()
        fvs.set_stand(stand, 'PN', 612, 6, 45, 'DF', 110)

        fvs.access_db('access_db', directory=path)
        fvs.sqlite_db('sqlite_db', directory=path)
        fvs.excel_db('excel_db', directory=path)

        end_message = """**WORKFLOW 6 created a FULL CRUISE stand from importing plot data from an excel sheet.

  It then ran the FVS module to create FVS formatted databases from the stand data. FVS is the US Forest Service's Forest Vegetation Simulator.

  Outputs:
      FVS Access database "access_db.db" from [fvs_class.access_db()] in desktop/treetopper_outputs/workflow_6/
      FVS Suppose file "Suppose.loc" in desktop/treetopper_outputs/workflow_6/. ** FVS Legacy needs a .loc file along with the database.
      FVS SQLite database "sqlite_db.db" from [fvs_class.sqlite_db()] in desktop/treetopper_outputs/workflow_6/
      FVS Excel database "excel_db.db" from [fvs_class.excel_db()] in desktop/treetopper_outputs/workflow_6/
      Plot data .xlsx "example_xlsx_export.xlsx" in desktop/treetopper_outputs/workflow_6/
"""
        print(f'\n\n{end_message}')


    def main(workflow_number):
        opts = {
            1: workflow_1,
            2: workflow_2,
            3: workflow_3,
            4: workflow_4,
            5: workflow_5,
            6: workflow_6
        }

        opts[workflow_number](workflow_number)


    main(wf)




