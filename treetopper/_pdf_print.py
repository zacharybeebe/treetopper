from fpdf import FPDF
from treetopper._constants import (format_comma,
                                   sort_grade,
                                   SORTED_HEADS,
                                   ALL_SPECIES_NAMES,
                                   LOG_LENGTHS)


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def compile_report(self, stand):
        self.set_font('Times', 'B', 10)
        height = 8

        self.cell(150, height, f'STAND REPORT FOR: {stand.name}', 0, 0, align='L')
        self.ln(height * 2)

        # Summary Table
        self.cell(50, height, 'STAND CONDITIONS', 0, 0, align='L')

        table_head = ['SPECIES'] + [head[1] for head in SORTED_HEADS]
        self.ln(height)

        spp_col = 18
        end_col = 21
        dat_col = 18
        metric_col = 24

        for i, tab in enumerate(table_head):
            self.set_font('Times', 'B', 7)
            if i == 0:
                self.cell(spp_col, height, tab, 1, 0, align='L')
            elif i >= len(table_head) - 2:
                self.cell(end_col, height, tab, 1, 0, align='C')
            else:
                self.cell(dat_col, height, tab, 1, 0, align='C')

        self.ln(height)

        table_data = self._get_species_table(stand.species)

        for i, row in enumerate(table_data):
            if i == len(table_data) - 1:
                self.set_font('Times', 'B', 8)
            else:
                self.set_font('Times', '', 8)
            for j, col in enumerate(row):
                if j == 0:
                    self.cell(spp_col, height, col, 1, 0, align='L')
                elif j >= len(row) - 2:
                    self.cell(end_col, height, col, 1, 0, align='C')
                else:
                    self.cell(dat_col, height, col, 1, 0, align='C')
            self.ln(height)

        self.add_page()
        self.set_font('Times', 'B', 10)
        self.cell(50, height, 'LOG TABLES', 0, 0, align='L')
        self.ln(height)

        spp_col = metric_col * 7
        log_tables = self._get_log_tables(stand.logs)

        for i, value in enumerate(log_tables):
            for j, table in enumerate(value):
                if j == 0:
                    if i > 0:
                        self.ln(height)
                    self.set_font('Times', 'B', 10)
                    self.cell(spp_col, height, table, 0, 0, align='L')
                    self.ln(height)
                else:
                    for k, row in enumerate(table):
                        if k == 0:
                            self.set_font('Times', 'B', 9)
                            self.cell(spp_col, height, row, 1, 0, align='C')
                            self.ln(height)
                        else:
                            if k == 1:
                                self.set_font('Times', 'B', 7)
                            elif k == len(table) - 1:
                                self.set_font('Times', 'B', 8)
                            else:
                                self.set_font('Times', '', 8)

                            for l, col in enumerate(row):
                                if l == 0:
                                    self.cell(metric_col, height, col, 1, 0, align='L')
                                else:
                                    self.cell(metric_col, height, col, 1, 0, align='C')
                            self.ln(height)
                    self.ln(height)
            self.add_page()
            if i < len(log_tables) - 1:
                self.set_font('Times', 'B', 10)
                self.cell(50, height, 'LOG TABLES', 0, 0, align='L')

        self.set_font('Times', 'B', 10)
        self.cell(50, height, 'STAND STATISTICS', 0, 0, align='L')
        self.ln(height)

        metric_col = 24
        spp_width = metric_col + ((end_col - 1) * 8)
        stats_data = self._get_species_stats_table(stand.species_stats)
        for i, table in enumerate(stats_data):
            for j, row in enumerate(table):
                if j == 0:
                    self.set_font('Times', 'B', 9)
                    self.cell(spp_width, height, row, 1, 0, align='C')
                else:
                    if j == 1:
                        self.set_font('Times', 'B', 7)
                    else:
                        self.set_font('Times', '', 8)
                    for k, col in enumerate(row):
                        if k == 0:
                            self.cell(metric_col, height, col, 1, 0, align='L')
                        else:
                            self.cell(end_col-1, height, col, 1, 0, align='C')
                self.ln(height)
            self.ln(height)

    def _get_species_table(self, species):
            table_data = []
            for spp in species:
                temp = []
                if spp == 'totals_all':
                    temp.append('TOTALS')
                else:
                    temp.append(spp)
                for i, sub in enumerate(SORTED_HEADS):
                    temp.append(format_comma(species[spp][sub[0]]))
                table_data.append(temp)
            table_data.append(table_data.pop(0))
            return table_data

    def _get_log_tables(self, logs):
        heads = ['LOG LENGTHS'] + [rng.upper() for rng in LOG_LENGTHS] + ['TOTALS']
        tables = [['bf_ac', 'BOARD FEET PER ACRE'], ['cf_ac', 'CUBIC FEET PER ACRE'], ['lpa', 'LOGS PER ACRE']]
        table_data = []

        for i in tables:
            temp = [i[1]]
            for species in logs:
                temp_temp = []
                if species == 'totals_all':
                    label = 'TOTAL SPECIES'
                else:
                    label = ALL_SPECIES_NAMES[species]

                temp_temp.append(label)
                temp_temp.append(heads)
                grade_sort = []
                for grade in logs[species]:
                    values = [logs[species][grade][rng][i[0]]['mean'] for rng in logs[species][grade]]
                    if sum(values) > 0:
                        if grade == 'totals_by_length':
                            txt = 'TOTALS'
                        else:
                            txt = grade
                        show2 = [txt] + [format_comma(z) for z in values]
                        grade_sort.append(show2)
                grade_sort = sorted(grade_sort, key=sort_grade)
                for g in grade_sort:
                    temp_temp.append(g)
                temp.append(temp_temp)

            if len(logs) <= 2:
                temp.pop(1)
            else:
                temp.append(temp.pop(1))

            table_data.append(temp)

        return table_data

    def _get_species_stats_table(self, species_stats):
        labels = {'tpa': 'TPA',
                  'ba_ac': 'BASAL AREA',
                  'rd_ac': 'RD',
                  'bf_ac': 'BOARD FEET',
                  'cf_ac': 'CUBIC FEET'}
        table_data = []
        for spp in species_stats:
            if spp == 'totals_all':
                show = 'TOTALS'
            else:
                show = ALL_SPECIES_NAMES[spp]
            temp = [show]
            heads = ['METRIC'] + [head.upper() for head in species_stats[spp]['tpa'] if head != 'low_avg_high'] + ['LOW', 'AVERAGE', 'HIGH']
            temp.append(heads)
            for key in species_stats[spp]:
                temp_temp = [labels[key]]
                for sub in species_stats[spp][key]:
                    data = species_stats[spp][key][sub]
                    if data == 'Not enough data':
                        temp_temp.append(data)
                        for i in range(6):
                            temp_temp.append('-')
                        break
                    else:
                        if sub != 'stderr_pct' and sub != 'low_avg_high':
                            temp_temp.append(format_comma(data))
                        elif sub == 'stderr_pct':
                            temp_temp.append(str(round(data, 1)) + ' %')
                        else:
                            for i in data:
                                temp_temp.append(format_comma(i))
                temp.append(temp_temp)
            table_data.append(temp)

        if len(species_stats) <= 2:
            table_data.pop(0)
        else:
            table_data.append(table_data.pop(0))

        return table_data

    def compile_thin_report(self, thin, message=None):
        self.set_font('Times', 'B', 10)
        height = 8
        species, min_dbh, max_dbh = thin._get_message_params_report()
        self.cell(150, height, f'THINNING TARGET: {thin.target} {thin.target_metric.replace("_", "/").upper()}', 0, 0, align='L')
        self.ln(height)
        self.cell(150, height, f'THINNING PARAMETERS:', 0, 0, align='L')
        self.ln(height)

        self.set_font('Times', 'B', 8)
        self.cell(150, height, f'    SPECIES: {", ".join(species)}', 0, 0, align='L')
        self.ln(height)
        self.cell(150, height, f'    MINIMUM DBH: {min_dbh}', 0, 0, align='L')
        self.ln(height)
        self.cell(150, height, f'    MAXIMUM DBH: {max_dbh}', 0, 0, align='L')
        self.ln(height * 2)

        spp_col = 18
        end_col = 21
        dat_col = 18
        metric_col = 24

        table_data = self._get_thin_species_table(thin.species_data)

        for i, condition in enumerate(table_data):
            for j, row in enumerate(condition):
                if j == 0:
                    self.set_font('Times', 'B', 10)
                    self.cell(50, height, f'{row}', 0, 0, align='L')
                    self.ln(height)

                    table_head = ['SPECIES'] + [head[1] for head in SORTED_HEADS]
                    for i, tab in enumerate(table_head):
                        self.set_font('Times', 'B', 7)
                        if i == 0:
                            self.cell(spp_col, height, tab, 1, 0, align='L')
                        elif i >= len(table_head) - 2:
                            self.cell(end_col, height, tab, 1, 0, align='C')
                        else:
                            self.cell(dat_col, height, tab, 1, 0, align='C')
                    self.ln(height)
                else:
                    if j == len(condition) - 1:
                        self.set_font('Times', 'B', 8)
                    else:
                        self.set_font('Times', '', 8)
                    for k, col in enumerate(row):
                        if k == 0:
                            self.cell(spp_col, height, col, 1, 0, align='L')
                        elif k >= len(row) - 2:
                            self.cell(end_col, height, col, 1, 0, align='C')
                        else:
                            self.cell(dat_col, height, col, 1, 0, align='C')
                    self.ln(height)
            self.ln(height)

        if message:
            self.set_font('Times', '', 10)
            for line in message:
                self.cell(250, height, line, 0, 0, align='L')
                self.ln(height)



    def _get_thin_species_table(self, species):
        table_data = []
        for condition in species:
            temp = [condition.replace('_', '').upper()]
            for spp in species[condition]:
                temp_temp = []
                if spp == 'totals_all':
                    temp_temp.append('TOTALS')
                else:
                    temp_temp.append(spp)
                for i, sub in enumerate(SORTED_HEADS):
                    temp_temp.append(format_comma(species[condition][spp][sub[0]]))
                temp.append(temp_temp)
            temp.append(temp.pop(1))
            table_data.append(temp)
        table_data.append(table_data.pop(1))
        return table_data
