from os import startfile, getcwd
from os.path import join
from _constants import (math,
                        extension_check,
                        LOG_LENGTHS)
from datetime import (datetime,
                      date)
from statistics import (mean,
                        variance,
                        stdev)
from plot import Plot
from timber import (TimberQuick,
                    TimberFull)
from thin import (ThinTPA,
                  ThinBA,
                  ThinRD)
from _import_from_sheets import (import_csv_quick,
                                 import_csv_full,
                                 import_excel_quick,
                                 import_excel_full)
from _testing import (generate_random_plots,
                      timer)
from _console_print import (print_species,
                            print_logs,
                            print_species_stats)
from _pdf_print import PDF
import plotly.express as px



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
        To create a formatted blank CSV or Excel file, open the terminal and type "python treetopper.blank_sheet.py" and
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

        HAPPY CRUISING!"""

    def __init__(self, name:str, acres:float = None, inventory_date:str = None):
        self.name = name
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
        """Prints a stand report to the console"""
        print()
        print('STAND METRICS')
        print_species(self.species)
        print('\n\n')
        print('LOG METRICS')
        print_logs(self.logs)
        print()
        print('STAND STATISTICS')
        print_species_stats(self.species_stats)

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
                plot.add_tree(TimberQuick(mets['species'], mets['dbh'], height, mets['plot_factor'],
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
                tree = TimberFull(mets['species'], mets['dbh'], height, mets['plot_factor'])
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
                plot.add_tree(TimberQuick(mets['species'], mets['dbh'], height, mets['plot_factor'],
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
                tree = TimberFull(mets['species'], mets['dbh'], height, mets['plot_factor'])
                for lnum in mets['logs']:
                    tree.add_log(*mets['logs'][lnum])
                plot.add_tree(tree)
            self.add_plot(plot)

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








"""EXAMPLE WORK FLOWS"""

if __name__ == '__main__':

    def workflow_1():
        """Workflow 1 will create a quick cruise stand from manually entered trees and plots and will then show a console report.

           Using the ThinTPA class, we will thin the stand to a Trees per Acre of 80 considering all species and diameter ranges
           and then will show a console report of the thinning"""

        stand = Stand('WF1')
        plot_factor = -20
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

        stand.console_report()

        thin80tpa = ThinTPA(stand, 80)
        thin80tpa.console_report()




    def workflow_2():
        """Workflow 2 will create a full cruise stand from manually entered trees and plots and will then show a console report.

           Using the ThinBA class, we will thin the stand to a BA/ac of 120 considering only DF and WH and all diameter ranges
           and then will show a console report of the thinning"""

        stand = Stand('WF2')
        plot_factor = 33.3
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

        stand.console_report()

        thin120ba = ThinBA(stand, 120, species_to_cut=['DF', 'WH'])
        thin120ba.console_report()


    def workflow_3():
        """Workflow 3 will create a quick cruise stand from importing a stand from a quick cruise Excel file and show a console report.
           The stand class' name needs to match the stand name within the Excel file, we will use "EX4". The Excel file we will be using is
           Example_Excel_quick.xlsx

           Using the ThinRD class, we will thin the stand to a RD/ac of 25 considering only DF and WH with a
           minimum diameter of 10 inches and a max of 18 inches, and then will show a console report of the thinning.

           ** Note this thinning density won't be able to be achieved fully because our parameters don't allow for the needed
           harvest density, but this is to illustrate that the thinning will let the user know how much density was taken and how much
           more is needed to achieve the desired density target"""

        stand = Stand('EX4')
        stand.from_excel_quick('Example_Excel_quick.xlsx')
        stand.console_report()

        thin25rd = ThinRD(stand, 25, species_to_cut=['DF', 'WH'], min_dbh_to_cut=10, max_dbh_to_cut=18)
        thin25rd.console_report()


    def workflow_4():
        """Workflow 4 will create a full cruise stand from importing a stand from a full cruise CSV file and show a console report.
           The stand class' name needs to match the stand name within the CSV file, we will use "OK2". The CSV file we will be using is
           Example_CSV_full.csv

           Using the ThinTPA class, we will thin the stand to a TPA of 100 considering all species and diameter ranges
           and then will TRY to show a console report of the thinning.

           ** Note this thinning density is greater than the entire stand's density and the Thin Class will throw a
           TargetDensityError exception which will explain what went wrong"""

        stand = Stand('OK2')
        stand.from_csv_full('Example_CSV_full.csv')
        stand.console_report()

        thin100tpa = ThinTPA(stand, 100)
        thin100tpa.console_report()

    def workflow_5():
        """Workflow 5 will create a full cruise stand from importing a stand from a full cruise CSV file and export a PDF report.
           The stand class' name needs to match the stand name within the CSV file, we will use "EX3". The CSV file we will be using is
           Example_CSV_quick.csv.

           The PDF will exported to the current working directory as 'stand_report.pdf'

           Using the ThinBA class, we will thin the stand to a BA/ac of 140 considering only DF, WH and RA
           with a maximum thinning DBH of 24 inches (thinning from below). Then a pdf report of the thinning will be exported
           in the current working directory as 'thin_report.pdf'"""

        stand = Stand('EX3')
        stand.from_csv_quick('Example_CSV_quick.csv')
        stand.pdf_report('stand_report.pdf')

        thin140ba = ThinBA(stand, 140, species_to_cut=['DF', 'WH', 'RA'], max_dbh_to_cut=24)
        thin140ba.pdf_report('thin_report.pdf')


    # workflow_1()
    # workflow_2()
    # workflow_3()
    # workflow_4()
    # workflow_5()




