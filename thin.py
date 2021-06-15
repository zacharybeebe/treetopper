
import math



class Thin(object):
    def __init__(self, stand, target_density: int, species_to_cut: list, min_dbh_to_cut: int, max_dbh_to_cut: int):
        self.stand = stand
        self.target = target_density
        self.min_dbh = min_dbh_to_cut
        self.max_dbh = max_dbh_to_cut
        self.species = species_to_cut

        self.keys = ['tpa', 'ba_ac', 'rd_ac', 'bf_ac', 'cf_ac']
        self.adds = [['ba_ac', 'ba_tree'], ['rd_ac', 'rd_tree'], ['bf_ac', 'bf_tree'], ['cf_ac', 'cf_tree']]

        self.cur_tpa = 0
        self.cur_ba_ac = 0
        self.cur_rd_ac = 0
        self.cur_bf_ac = 0
        self.cur_cf_ac = 0

        self.res_tpa = 0
        self.res_ba_ac = 0
        self.res_rd_ac = 0
        self.res_bf_ac = 0
        self.res_cf_ac = 0

        self.rem_tpa = 0
        self.rem_ba_ac = 0
        self.rem_rd_ac = 0
        self.rem_bf_ac = 0
        self.rem_cf_ac = 0

        self.trees = self.aggregate_trees()


        print(f'Target: {self.target}')
        for key in self.keys:
            print(f'Thin Current {key}: {round(getattr(self, f"cur_{key}"))}')
            #print(f'Stand {key}: {self.stand[key]}')

    def __getitem__(self, attribute: str):
        return self.__dict__[attribute]


    def aggregate_trees(self):
        dbh = {}
        for plot in self.stand.plots:
            for tree in plot.trees:
                d = int(tree.dbh)
                if tree.species not in dbh:
                    dbh[tree.species] = {}
                if d not in dbh[tree.species]:
                    dbh[tree.species][d] = {key: 0 for key in self.keys}

                for key in self.keys:
                    dbh[tree.species][d][key] += tree[key] / self.stand.plot_count
                    setattr(self, f'cur_{key}', getattr(self, f'cur_{key}') + (tree[key] / self.stand.plot_count))

        for spp in dbh:
            for d in dbh[spp]:
                for add in self.adds:
                    dbh[spp][d][add[1]] = dbh[spp][d][add[0]] / dbh[spp][d]['tpa']

        return dbh

    def thin_to_target(self, target_metric):
        if self.species == 'all':
            species = [spp for spp in self.trees if spp != 'totals_all']
            ratio = self.target / self[f'cur_{target_metric}']
        else:
            species = self.species
            sums = []
            for spp in self.trees:
                if spp in species:
                    for d in self.trees[spp]:
                        if self.min_dbh <= d <= self.max_dbh:
                            sums.append(self.trees[spp][d][target_metric])
            s = sum(sums)
            if s < self.target:
                ratio = 0
            else:
                ratio = self.target / sum(sums)

        for spp in self.trees:
            if spp in species:
                for d in self.trees[spp]:
                    if self.min_dbh <= d <= self.max_dbh:
                        residual_tpa = ratio * self.trees[spp][d]['tpa']
                        removal_tpa = (1 - ratio) * self.trees[spp][d]['tpa']
                        for key in self.adds:
                            residual = self.trees[spp][d][key[1]] * residual_tpa
                            removal = self.trees[spp][d][key[1]] * removal_tpa
                            setattr(self, f'res_{key[0]}', getattr(self, f'res_{key[0]}') + residual)
                            setattr(self, f'rem_{key[0]}', getattr(self, f'rem_{key[0]}') + removal)
                        self.res_tpa += residual_tpa
                        self.rem_tpa += removal_tpa
            else:
                for d in self.trees[spp]:
                    for key in self.adds:
                        setattr(self, f'res_{key[0]}', getattr(self, f'res_{key[0]}') + self.trees[spp][d][key[1]])
                        self.res_tpa += self.trees[spp][d]['tpa']


        res_qmd = math.sqrt((self.res_ba_ac / self.res_tpa) / .005454)
        print(f'\nRES QMD: {res_qmd}')
        print(f'RES BA_AC: {self.res_ba_ac}')

        print(f'Calc Resid RD: {self.res_ba_ac / math.sqrt(res_qmd)}')

        print(f'\nTarget: {self.target}')
        for i in [['rem_', 'Remove'], ['res_', 'Residual']]:
            for key in self.keys:
                print(f'Thin {i[1]} {key}: {round(getattr(self, f"{i[0]}{key}"))}')
            print()
        print(f'\nratio: {ratio}')



class ThinTPA(Thin):
    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinTPA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.thin_to_target('tpa')

class ThinBA(Thin):
    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinBA, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.thin_to_target('ba_ac')

class ThinRD(Thin):
    def __init__(self, stand, target_density: int, species_to_cut: list = 'all', min_dbh_to_cut: int = 0, max_dbh_to_cut: int = 999):
        super(ThinRD, self).__init__(stand, target_density, species_to_cut, min_dbh_to_cut, max_dbh_to_cut)
        self.thin_to_target('rd_ac')








