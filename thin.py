from os import startfile, getcwd
from os.path import join
from copy import deepcopy
from statistics import mean
import math
from _console_print import print_thin_species
from _pdf_print import PDF
from _constants import extension_check


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

        self.full_thin = [True, None, None]

        self.keys = ['tpa', 'ba_ac', 'rd_ac', 'bf_ac', 'cf_ac']
        self.adds = [['ba_ac', 'ba_tree'], ['rd_ac', 'rd_tree'], ['bf_ac', 'bf_tree'], ['cf_ac', 'cf_tree']]
        self.conditions = ['current_', 'residual_', 'removal_']

        for key in self.keys:
            setattr(self, f'{self.conditions[0]}{key}', 0)

        self.trees = self.aggregate_trees()

    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]

    def aggregate_trees(self):
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

    def thin_to_target(self, target_metric):
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

    def _update_species_conditions_dict(self, master_condition_species, trees):
        """Updates the species data dictionary being compiled in self._get_species_conditions(), used internally"""
        master_condition_species.update({'qmd': math.sqrt((master_condition_species['ba_ac'] / master_condition_species['tpa']) / 0.005454)})
        master_condition_species.update({'vbar': master_condition_species['bf_ac'] / master_condition_species['ba_ac']})
        master_condition_species.update({'avg_hgt': mean([tree.height for tree in trees])})
        master_condition_species.update({'hdr': mean([tree.hdr for tree in trees])})

    def console_report(self):
        """Prints a report to the console of the stands conditions: current, removals, and residual shown by species and totals"""
        species, min_dbh, max_dbh = self._get_message_params_report()
        if not self.full_thin[0]:
            needed = round(self[f'current_{self.full_thin[2]}'] - self.target)
            message = f"""\n** COULD NOT ACHIEVE TARGET DENSITY OF {self.target} {self.full_thin[2].replace('_', ' ').upper()} **
** THINNING PARAMETERS ONLY ALLOWED {round(self.full_thin[1], 1)} {self.full_thin[2].replace('_', '/').upper()} OF THE {needed} NEEDED TO BE HARVESTED **
   THINNING PARAMETERS:
   \tSPECIES: {', '.join(species)}
   \tMIN DBH: {min_dbh}
   \tMAX DBH: {max_dbh}\n"""
            print(message)
            print_thin_species(self.species_data)
        else:
            message = f"""\nTARGET DENSITY OF {self.target} {self.full_thin[2].replace('_', '/').upper()} ACHIEVED
THINNING PARAMETERS:
   \tSPECIES: {', '.join(species)}
   \tMIN DBH: {min_dbh}
   \tMAX DBH: {max_dbh}\n"""
            print(message)
            print_thin_species(self.species_data)

    def pdf_report(self, filename: str, directory: str = None):
        """Exports a pdf of the thinning report to a user specified directory or if directory is None, to the current working directory"""
        if not self.full_thin[0]:
            needed = round(self[f'current_{self.full_thin[2]}'] - self.target)
            l1 = f"""** COULD NOT ACHIEVE TARGET DENSITY OF {self.target} {self.full_thin[2].replace('_', ' ').upper()} **"""
            l2 = f"""** THINNING PARAMETERS ONLY ALLOWED {round(self.full_thin[1], 1)} {self.full_thin[2].replace('_', '/').upper()} OF THE {needed} NEEDED TO BE HARVESTED **"""
            message = [l1, l2]
        else:
            message = None

        check = extension_check(filename, '.pdf')
        if directory:
            file = join(directory, check)
        else:
            file = join(getcwd(), check)
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.compile_thin_report(self, message=message)
        pdf.output(file, 'F')
        startfile(file)

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

    def check_density(self):
        """Will check to see if the target density is in fact lower than the total stand density. If the target density is higher,
           it will throw a custom exception: TargetDensityError"""
        current_density = self[f'current_{self.target_metric}']
        met = self.target_metric.replace('_', '/').upper()
        if current_density < self.target:
            raise TargetDenistyError(self.target, current_density, met)


class ThinTPA(Thin):
    """Thin by Trees per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinTPA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'tpa'
        self.check_density()
        self.thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()


class ThinBA(Thin):
    """Thin by Basal Area per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinBA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'ba_ac'
        self.check_density()
        self.thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()


class ThinRD(Thin):
    """Thin by Relative Density per Acre"""

    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinRD, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.target_metric = 'rd_ac'
        self.check_density()
        self.thin_to_target(self.target_metric)
        self.species_data = self._get_species_conditions()


class TargetDenistyError(Exception):
    def __init__(self, target_density, current_density, target_metric):
        p1 = f"""Target Density of {target_density} {target_metric} """
        p2 = f"""is greater than Stand Total of {round(current_density, 1)} {target_metric}. """
        p3 = f"""Please lower Target Density"""
        self.message = p1 + p2 + p3
        super(TargetDenistyError, self).__init__(self.message)



if __name__ == '__main__':
    from stand import Stand

    stand = Stand('OK2', 46.94)
    stand.from_csv_full('../example_csv_and_xlsx/Example_CSV_full.csv')

    thin = ThinBA(stand, 160)
    thin.console_report()









