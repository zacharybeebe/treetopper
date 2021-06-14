from random import randrange
from statistics import mean
from timber import (math,
                    TimberQuick,
                    TimberFull,
                    GRADE_NAMES,
                    LOG_LENGTHS)
from _testing import generate_random_trees_quick
from _console_print import print_plot_logs


class Plot(object):
    def __init__(self):
        self.trees = []
        self.tree_count = 0
        self.tpa = 0
        self.ba_ac = 0
        self.qmd = 0
        self.rd_ac = 0
        self.bf_ac = 0
        self.cf_ac = 0
        self.avg_hgt = 0
        self.vbar = 0
        self.metrics = ['tpa', 'ba_ac', 'rd_ac', 'bf_ac', 'cf_ac']

        self.species = {'totals_all': self._format_species_dict()}
        self.logs = {'totals_all': self._format_logs_species_dict()}

    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]

    def add_tree(self, timber):
        self.trees.append(timber)
        self.tree_count += 1

        for met in self.metrics:
            setattr(self, met, getattr(self, met) + timber[met])

        self.qmd = math.sqrt((self.ba_ac / self.tpa) / .005454)
        self.vbar = self.bf_ac / self.ba_ac
        self.avg_hgt = mean([t.height for t in self.trees])
        self.hdr = mean([t.hdr for t in self.trees])

        self._update_species(timber)

        for l_num in timber.logs:
            log = timber.logs[l_num]
            if log.species not in self.logs:
                self.logs[log.species] = self._format_logs_species_dict()
            self._update_logs(log)

    def _format_logs_species_dict(self):
        master = {}
        sub = {'lpa': 0,
               'bf_ac': 0,
               'cf_ac': 0}
        for grade in GRADE_NAMES:
            master[grade] = {rng: sub.copy() for rng in LOG_LENGTHS}
            master[grade].update({'totals_by_grade': sub.copy()})
            master[grade].update({'display': False})
        master['totals_by_length'] = {rng: sub.copy() for rng in LOG_LENGTHS}
        master['totals_by_length'].update({'totals_by_grade': sub.copy()})
        master['totals_by_length'].update({'display': False})
        return master

    def _update_logs(self, log):
        for key in [log.species, 'totals_all']:
            for sub in ['lpa', 'bf_ac', 'cf_ac']:
                self.logs[key][log.grade][log.length_range][sub] += log[sub]
                self.logs[key][log.grade]['totals_by_grade'][sub] += log[sub]
                self.logs[key][log.grade]['display'] = True
                self.logs[key]['totals_by_length'][log.length_range][sub] += log[sub]
                self.logs[key]['totals_by_length']['totals_by_grade'][sub] += log[sub]
                self.logs[key]['totals_by_length']['display'] = True

    def _format_species_dict(self):
        master = {'tpa': 0,
                  'ba_ac': 0,
                  'qmd': 0,
                  'avg_hgt': 0,
                  'hdr': 0,
                  'rd_ac': 0,
                  'bf_ac': 0,
                  'cf_ac': 0,
                  'vbar': 0}
        return master

    def _update_species(self, tree):
        update_after = ['qmd', 'vbar', 'avg_hgt', 'hdr']
        if tree.species not in self.species:
            self.species[tree.species] = self._format_species_dict()

        for key in self.species[tree.species]:
            if key not in update_after:
                self.species[tree.species][key] += tree[key]
                self.species['totals_all'][key] += tree[key]

        for key in [tree.species, 'totals_all']:
            self.species[key]['qmd'] = math.sqrt((self.species[key]['ba_ac'] / self.species[key]['tpa']) / .005454)
            self.species[key]['vbar'] = self.species[key]['bf_ac'] / self.species[key]['ba_ac']
            if key == 'totals_all':
                self.species[key]['avg_hgt'] = mean([t.height for t in self.trees])
                self.species[key]['hdr'] = mean([t.hdr for t in self.trees])
            else:
                self.species[key]['avg_hgt'] = mean([t.height for t in self.trees if t.species == tree.species])
                self.species[key]['hdr'] = mean([t.hdr for t in self.trees if t.species == tree.species])







if __name__ == '__main__':
    trees, tree_count = generate_random_trees_quick(randrange(4, 9))

    plot = Plot()
    for tree in trees:
        plot.add_tree(tree)

    print(f'Plot TreeCount: {len(trees)}')
    print(f'Plot TPA: {plot.tpa}')
    print(f'Plot BA_AC: {plot.ba_ac}')
    print(f'Plot BF_AC: {plot.bf_ac}')
    print(f'Plot AVG_HGT: {plot.avg_hgt}')
    print(f'Plot HDR: {plot.hdr}')
    print()

    # for species in plot.species:
    #     print(f'{species}:')
    #     for key in plot.species[species]:
    #         print(f'\t{key}: {plot.species[species][key]}')


    for i, tree in enumerate(plot.trees):
        print(f'Tree #{i+1}')
        print(f'\tSpecies: {tree.species}')
        print(f'\tDBH: {tree.dbh}')
        print(f'\tHeight: {tree.height}')
        print(f'\tHDR: {tree.hdr}')
        print(f'\tBF_AC: {tree.bf_ac}')
        print(f'\tLOGS: {tree.logs}')
    print()

    print_plot_logs(plot)





