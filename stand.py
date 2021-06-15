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
        self.plots.append(plot)
        self.plot_count += 1
        for met in self.metrics:
            self._update_metrics(met)
        self.qmd = math.sqrt((self.ba_ac / self.tpa) / .005454)
        self.vbar = self.bf_ac / self.ba_ac
        self._update_species(plot)
        self._update_logs(plot)

    def from_csv_quick(self, directory):
        plots, avg_hdr = import_csv_quick(directory, self.name)
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

    def from_csv_full(self, directory):
        plots, avg_hdr = import_csv_full(directory, self.name)
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
                tree.calc_volume_and_logs()
                plot.add_tree(tree)
            self.add_plot(plot)

    def from_excel_quick(self, directory):
        plots, avg_hdr = import_excel_quick(directory, self.name)
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

    def from_excel_full(self, directory):
        plots, avg_hdr = import_excel_full(directory, self.name)
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
                tree.calc_volume_and_logs()
                plot.add_tree(tree)
            self.add_plot(plot)

    def _update_metrics(self, metric: str):
        metric_list = [plot[metric] for plot in self.plots]
        stats = self._get_stats(metric_list)
        setattr(self, metric, stats['mean'])
        setattr(self, f'{metric}_stats', stats)

    def _update_species(self, plot):
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
    stand = Stand('EX1')

    # f_stands[f].from_csv_full('stand_data_C_full.csv')
    stand.from_excel_quick('stand_data_E_quick.xlsx')

    target = 140
    print('Thin ALL')
    thinba = ThinBA(stand, target)
    print('\nThin DF/WH')
    thinbaspp = ThinBA(stand, target, ['DF', 'WH'])
    print('\nThin ALL Min 10 Max 18')
    thinbadbh = ThinBA(stand, target, species_to_cut='all', min_dbh_to_cut=10, max_dbh_to_cut=18)
    print('\nThin DF/WH min 10 Max 18')
    thinbasppdbh = ThinBA(stand, target, ['DF', 'WH'], min_dbh_to_cut=10, max_dbh_to_cut=18)


    # stand.console_report()
    # stand.pdf_report('test1')



    # times = {'count': [],
    #          'times': []}
    # @timer
    # def generate_add_plots(stand, min, max, times):
    #     plots, tree_count = generate_random_plots(randrange(min,max), full=True)
    #
    #     for i, plot in enumerate(plots):
    #         times['count'].append(i)
    #         times['times'].append(stand.add_plot(plot)[1])
    #     return tree_count
    #
    # tree_count = generate_add_plots(stand, 15, 20, times)
    # print(f'Trees: {tree_count}\n')
    #
    # stand.console_report()
    #
    #
    # fig = px.scatter(times, x='times', y='count')
    # fig.show()



