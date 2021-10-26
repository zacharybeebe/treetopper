import math
from os import startfile, getcwd
from os.path import join
from copy import deepcopy
from statistics import mean

from treetopper._exceptions import TargetDensityError
from treetopper._constants import SORTED_HEADS
from treetopper._print_console import print_thin
from treetopper._print_pdf import PDF
from treetopper._utils import (
    extension_check,
    format_comma
)

NOT_FULL_THIN_MESSAGE = """
** COULD NOT ACHIEVE TARGET DENSITY OF {target} {thin_param} **
** THINNING PARAMETERS ONLY ALLOWED {actual} {thin_param} OF THE {needed} {thin_param} NEEDED TO BE HARVESTED **
   THINNING PARAMETERS:
   \tSPECIES: {species}
   \tMIN DBH: {min_dbh}
   \tMAX DBH: {max_dbh}
"""

SUCCESS_MESSAGE = """
TARGET DENSITY OF {target} {thin_param} ACHIEVED
THINNING PARAMETERS:
   \tSPECIES: {species}
   \tMIN DBH: {min_dbh}
   \tMAX DBH: {max_dbh}
"""


class Thin(object):
    """The Thin Class is the parent class of the three thinning child classes: ThinTPA, ThinBA, and ThinRD.

       The thinning classes create a deepcopy of the stand class so as not to disrupt any of the tree information.

       The thinning classes start to thin the stand by getting a dictionary of whole-number diameters based on species,
       these contain per-diameter metrics such as tpa, ba_ac, rd_ac, bf_ac..., and these metrics, other than tpa,
       also have a corresponding metric per tree value, by dividing the per-diameter metric by the per-diameter tpa.

       The thinnings then calculate a harvest-ratio to lower the stand's density to the target density, in accordance to the
       species and diameter limitations (if any). The harvest ratio is used to calculate the removal and residual per-diameter TPAs,
       which are then used to calculate the other removal and residual per-diameter metrics by multiplying the respective TPAs by the
       per-diameter metric per tree values"""

    def __init__(self, stand, target_density: int, species_to_cut: list, min_dbh_to_cut: int, max_dbh_to_cut: int):
        self.stand = deepcopy(stand)
        self.target = target_density
        self.min_dbh = min_dbh_to_cut
        self.max_dbh = max_dbh_to_cut
        self.species = species_to_cut

        self.species_data = None
        self.target_metric = None
        self.summary_thin = None
        self.report_message = None

        self.full_thin = [True, None, None]

        self.keys = ['tpa', 'ba_ac', 'rd_ac', 'bf_ac', 'cf_ac']
        self.adds = [['ba_ac', 'ba_tree'], ['rd_ac', 'rd_tree'], ['bf_ac', 'bf_tree'], ['cf_ac', 'cf_tree']]
        self.conditions = ['current_', 'residual_', 'removal_']

        for key in self.keys:
            setattr(self, f'{self.conditions[0]}{key}', 0)

        self.trees = self._aggregate_trees()

    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]

    def get_console_report_text(self):
        """Returns a console-formatted string of the thinning report"""
        return self._compile_console_report_text()

    def console_report(self):
        """Prints a console-formatted string of the thinning report"""
        print(self._compile_console_report_text())

    def pdf_report(self, filename: str, directory: str = None, start_file_upon_creation: bool = False):
        """Exports a pdf of the thinning report to a user specified directory or if directory is None, to the current working directory"""
        check = extension_check(filename, '.pdf')
        if directory:
            file = join(directory, check)
        else:
            file = join(getcwd(), check)
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.compile_thin_report(self)
        pdf.output(file, 'F')

        if start_file_upon_creation:
            startfile(file)

    def _aggregate_trees(self):
        """Returns the compiled whole-number diameters dictionary separated by species"""
        cur = self.conditions[0]
        tree_dbh_data = {}
        for plot in self.stand.plots:
            for tree in plot.trees:
                d = int(tree.dbh)
                if tree.species not in tree_dbh_data:
                    tree_dbh_data[tree.species] = {}
                if d not in tree_dbh_data[tree.species]:
                    tree_dbh_data[tree.species][d] = {}
                    for condition in self.conditions:
                        tree_dbh_data[tree.species][d][condition] = {key: 0 for key in self.keys}
                    tree_dbh_data[tree.species][d].update({'trees': []})
                for key in self.keys:
                    tree_dbh_data[tree.species][d][cur][key] += tree[key] / self.stand.plot_count
                    setattr(self, f'{cur}{key}', getattr(self, f'{cur}{key}') + (tree[key] / self.stand.plot_count))
                tree_dbh_data[tree.species][d]['trees'].append(tree)

        for spp in tree_dbh_data:
            for d in tree_dbh_data[spp]:
                for add in self.adds:
                    tree_dbh_data[spp][d][cur][add[1]] = tree_dbh_data[spp][d][cur][add[0]] / tree_dbh_data[spp][d][cur]['tpa']
        return tree_dbh_data

    def _thin_to_target(self, target_metric):
        """Calculates the harvest ratio to produce the target density and then modifies the dictionary
           self.trees (which was created by self.aggregate_trees()) to the correct removal and residual values"""
        cur, res, rem = self.conditions

        if self.species == 'all':
            species = [spp for spp in self.trees]
        else:
            species = self.species
        sums = []
        for spp in self.trees:
            if spp in species:
                for d in self.trees[spp]:
                    if self.min_dbh <= d <= self.max_dbh:
                        sums.append(self.trees[spp][d][cur][target_metric])
        s = sum(sums)
        target_ratio = 1 - ((self[f'{cur}{target_metric}'] - self.target) / s)
        if target_ratio < 0:
            ratio = 0
            self.full_thin = [False, s, target_metric]
        else:
            ratio = target_ratio
            self.full_thin = [True, s, target_metric]

        for spp in self.trees:
            if spp in species:
                for d in self.trees[spp]:
                    if self.min_dbh <= d <= self.max_dbh:
                        self.trees[spp][d][res]['tpa'] = ratio * self.trees[spp][d][cur]['tpa']
                        self.trees[spp][d][rem]['tpa'] = (1 - ratio) * self.trees[spp][d][cur]['tpa']
                        for condition in self.conditions[1:]:
                            for add in self.adds:
                                self.trees[spp][d][condition][add[0]] = self.trees[spp][d][cur][add[1]] * self.trees[spp][d][condition]['tpa']
                    else:
                        for add in self.adds:
                            self.trees[spp][d][res][add[0]] = self.trees[spp][d][cur][add[0]]
                        self.trees[spp][d][res]['tpa'] = self.trees[spp][d][cur]['tpa']
            else:
                for d in self.trees[spp]:
                    for add in self.adds:
                        self.trees[spp][d][res][add[0]] = self.trees[spp][d][cur][add[0]]
                    self.trees[spp][d][res]['tpa'] = self.trees[spp][d][cur]['tpa']

    def _get_species_conditions(self):
        """Returns an dictionary composed of the aggregate of the species totaled from the per-diameter values of the
           resultant self.trees (modified from self.thin_to_target())"""
        master = {}
        for condition in self.conditions:
            total_trees = []
            master[condition] = {'totals_all': {key: 0 for key in self.keys}}
            for spp in self.trees:
                trees = []
                master[condition][spp] = {key: 0 for key in self.keys}
                for d in self.trees[spp]:
                    for tree in self.trees[spp][d]['trees']:
                        if condition == 'current_':
                            trees.append(tree)
                            total_trees.append(tree)
                        elif condition == 'residual_':
                            d_rng = [d for d in self.trees[spp]]
                            min_ = min(d_rng)
                            max_ = max(d_rng)
                            if self.min_dbh <= min_ and self.max_dbh >= max_:
                                trees.append(tree)
                                total_trees.append(tree)
                            else:
                                if d < self.min_dbh or d > self.max_dbh:
                                    trees.append(tree)
                                    total_trees.append(tree)
                        else:
                            if self.min_dbh <= d <= self.max_dbh:
                                trees.append(tree)
                                total_trees.append(tree)
                    for key in self.keys:
                        master[condition][spp][key] += self.trees[spp][d][condition][key]
                        master[condition]['totals_all'][key] += self.trees[spp][d][condition][key]

                if master[condition][spp]['tpa'] > 0:
                    self._update_species_conditions_dict(master[condition][spp], trees)
                else:
                    del master[condition][spp]
            self._update_species_conditions_dict(master[condition]['totals_all'], total_trees)
        return master

    def _get_summary_tables(self):
        """Return a dict of data tables based on thinning conditions (Current Conditions, Removals, Residual Conditions)"""
        tables = {
            'current_': 'CURRENT CONDITIONS',
            'removal_': 'REMOVALS',
            'residual_': 'RESIDUAL CONDITIONS'
        }
        master = {}
        heads = ['SPECIES'] + [i[1] for i in SORTED_HEADS]
        for condition in tables:
            master[tables[condition]] = []
            for species in self.species_data[condition]:
                temp = ['TOTALS' if species == 'totals_all' else species]
                for sub, _ in SORTED_HEADS:
                    temp.append(format_comma(self.species_data[condition][species][sub]))
                master[tables[condition]].append(temp)
            master[tables[condition]].append(master[tables[condition]].pop(0))
            master[tables[condition]].insert(0, heads)
        return master

    def _get_message_params_report(self):
        """Returns the thinning parameters, formatted to be displayed in the console report or print report"""
        if self.species == 'all':
            species = [spp for spp in self.trees]
        else:
            species = self.species

        if self.min_dbh == 0:
            min_dbh = 'No Minimum'
        else:
            min_dbh = f'{self.min_dbh} inches'

        if self.max_dbh == 999:
            max_dbh = 'No Maximum'
        else:
            max_dbh = f'{self.max_dbh} inches'
        return species, min_dbh, max_dbh

    def _check_density(self):
        """Will check to see if the target density is in fact lower than the total stand density. If the target density is higher,
           it will throw a custom exception: TargetDensityError"""
        current_density = self[f'current_{self.target_metric}']
        met = self.target_metric.replace('_', '/').upper()
        if current_density < self.target:
            raise TargetDensityError(self.target, current_density, met)

    def _compile_console_report_text(self):
        """Returns a console-formatted string of the stands conditions: current, removals, and residual shown by species and totals,
        to be called by the standard print() function"""
        console_text = '\nTHINNING RESULTS\n'
        console_text += f'{self.report_message}\n'
        console_text += print_thin(self.summary_thin)
        return console_text

    def _get_report_message(self):
        species, min_dbh, max_dbh = self._get_message_params_report()
        thin_param = self.full_thin[2].replace('_', '/').upper()
        if not self.full_thin[0]:
            needed = round(self[f'current_{self.full_thin[2]}'] - self.target, 1)
            report_message = NOT_FULL_THIN_MESSAGE.format(target=self.target, thin_param=thin_param,
                                                          actual=round(self.full_thin[1], 1), needed=needed,
                                                          species=', '.join(species), min_dbh=min_dbh, max_dbh=max_dbh)
        else:
            report_message = SUCCESS_MESSAGE.format(target=self.target, thin_param=thin_param, species=', '.join(species),
                                                    min_dbh=min_dbh, max_dbh=max_dbh)
        return report_message

    @staticmethod
    def _update_species_conditions_dict(master_condition_species, trees):
        """Updates the species data dictionary being compiled in self._get_species_conditions(), used internally"""
        master_condition_species.update({'qmd': math.sqrt((master_condition_species['ba_ac'] / master_condition_species['tpa']) / 0.005454)})
        master_condition_species.update({'vbar': master_condition_species['bf_ac'] / master_condition_species['ba_ac']})
        master_condition_species.update({'avg_hgt': mean([tree.height for tree in trees])})
        master_condition_species.update({'hdr': mean([tree.hdr for tree in trees])})


class ThinTPA(Thin):
    """Thin by Trees per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinTPA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'tpa'
        self._check_density()
        self._thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()
        self.summary_thin = self._get_summary_tables()
        self.report_message = self._get_report_message()


class ThinBA(Thin):
    """Thin by Basal Area per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinBA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'ba_ac'
        self._check_density()
        self._thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()
        self.summary_thin = self._get_summary_tables()
        self.report_message = self._get_report_message()


class ThinRD(Thin):
    """Thin by Relative Density per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinRD, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'rd_ac'
        self._check_density()
        self._thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()
        self.summary_thin = self._get_summary_tables()
        self.report_message = self._get_report_message()


if __name__ == '__main__':
    from treetopper.stand import Stand

    stand = Stand('OK2', 46.94)
    stand.import_sheet_full('./example_csv_and_xlsx/Example_CSV_full.csv')

    thin = ThinBA(stand, 160)

    thin.console_report()
    thin.pdf_report('thin_test', start_file_upon_creation=True)









