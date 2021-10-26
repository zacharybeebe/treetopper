from fpdf import FPDF


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def compile_stand_report(self, stand):
        table_width = 190

        font_family = 'Arial'
        self.set_font(font_family, 'B', 10)
        height = 8

        self.cell(table_width, height, f'STAND REPORT FOR: {stand.name}', 0, 0, align='L')
        self.ln(height * 2)

        # Summary Table
        self.cell(table_width, height, 'STAND METRICS', 0, 0, align='C')
        self.ln(height)

        col_width = int(table_width / len(stand.summary_stand[0]))
        for i, row in enumerate(stand.summary_stand):
            if i == 0:
                self.set_font(font_family, 'B', 7)
            elif i == len(stand.summary_stand) - 1:
                self.set_font(font_family, 'B', 8)
            else:
                self.set_font(font_family, '', 8)

            for j, col in enumerate(row):
                if j == 0:
                    self.cell(col_width, height, col, 1, 0, align='L')
                else:
                    self.cell(col_width, height, col, 1, 0, align='C')
            self.ln(height)

        self.ln(height * 3)

        # Logs Tables [Board Feet per Acre, Cubic Feet per Acre, Logs per Acres]
        self.set_font(font_family, 'B', 10)
        self.cell(table_width, height, 'LOG METRICS', 0, 0, align='C')
        self.ln(height)

        for log_table in stand.summary_logs:
            self.set_font(font_family, 'B', 9)
            self.cell(50, height, log_table, 0, 0, align='L')
            self.ln(height)

            for species in stand.summary_logs[log_table]:
                col_len = len(stand.summary_logs[log_table][species][0])
                col_width = int(table_width / col_len)
                self.set_font(font_family, 'B', 8)

                self.cell(col_width * col_len, height, species, 1, 0, align='C')
                self.ln(height)
                for i, row in enumerate(stand.summary_logs[log_table][species]):
                    if i == 0 or i == len(stand.summary_logs[log_table][species]) - 1:
                        self.set_font(font_family, 'B', 8)
                    else:
                        self.set_font(font_family, '', 8)
                    for j, col in enumerate(row):
                        if j == 0:
                            self.cell(col_width, height, col, 1, 0, align='L')
                        else:
                            self.cell(col_width, height, col, 1, 0, align='C')
                    self.ln(height)
                self.ln(height)
            self.ln(height)

        self.ln(height * 2)

        # Statistics Tables by Species
        self.set_font(font_family, 'B', 10)
        self.cell(table_width, height, 'STAND STATISTICS', 0, 0, align='C')
        self.ln(height)

        for species in stand.summary_stats:
            col_len = len(stand.summary_stats[species][0])
            col_width = int(table_width / col_len)
            self.set_font(font_family, 'B', 8)

            self.cell(col_width * col_len, height, species, 1, 0, align='C')
            self.ln(height)
            self.set_font(font_family, '', 8)

            for row in stand.summary_stats[species]:
                for j, col in enumerate(row):
                    if j == 0:
                        self.cell(col_width, height, col, 1, 0, align='L')
                    else:
                        self.cell(col_width, height, col, 1, 0, align='C')
                self.ln(height)
            self.ln(height)

    def compile_thin_report(self, thin):
        table_width = 190

        font_family = 'Arial'
        self.set_font(font_family, 'B', 10)
        height = 8

        self.cell(table_width, height, f'THINNING REPORT FOR: {thin.stand.name}', 0, 0, align='L')
        self.ln(height * 2)

        message = [i.strip('\t') for i in thin.report_message.split('\n')]
        message.pop(0)
        self.set_font(font_family, 'B', 9)
        for i, mes in enumerate(message):
            if i > 0:
                self.set_font(font_family, 'B', 8)
            self.cell(table_width, height, mes, 0, 0, align='L')
            self.ln(height)

        self.ln(height)

        # Thin Summary Tables by Thin Condition
        for condition in thin.summary_thin:
            col_len = len(thin.summary_thin[condition][0])
            col_width = int(table_width / col_len)
            self.set_font(font_family, 'B', 8)

            self.cell(col_width * col_len, height, condition, 1, 0, align='C')
            self.ln(height)
            for i, row in enumerate(thin.summary_thin[condition]):
                if i == 0:
                    self.set_font(font_family, 'B', 7)
                elif i == len(thin.summary_thin[condition]) - 1:
                    self.set_font(font_family, 'B', 8)
                else:
                    self.set_font(font_family, '', 8)
                for j, col in enumerate(row):
                    if j == 0:
                        self.cell(col_width, height, col, 1, 0, align='L')
                    else:
                        self.cell(col_width, height, col, 1, 0, align='C')
                self.ln(height)
            self.ln(height)





