# treetopper
Python module for calculating Stand data using tree species of the west coast.

DOCUMENTATION
https://zacharybeebe.github.io/treetopper/

pip install treetopper


If you would like to download a blank, formatted inventory .csv or .xlsx...
    In the terminal

        pip install treetopper [if you haven't already]
        python -m treetopper.blank_sheet

    And follow the prompts


The species available for calculation are below and must have the correct species code...

        'DF': 'DOUGLAS-FIR'
        'WH': 'WESTERN HEMLOCK'
        'RC': 'WESTERN REDCEDAR'
        'SS': 'SITKA SPRUCE'
        'ES': 'ENGLEMANN SPRUCE'
        'SF': 'SILVER FIR'
        'GF': 'GRAND FIR'
        'NF': 'NOBLE FIR'
        'WL': 'WESTERN LARCH'
        'WP': 'WHITE PINE'
        'PP': 'PONDEROSA PINE'
        'LP': 'LODGEPOLE PINE'
        'JP': 'JEFFERY PINE'
        'SP': 'SUGAR PINE'
        'WF': 'WHITE FIR'
        'RF': 'RED FIR'
        'RW': 'COASTAL REDWOOD'
        'IC': 'INSENCE CEDAR'
        'RA': 'RED ALDER'
        'BM': 'BIGLEAF MAPLE'
        'CW': 'BLACK COTTONWOOD'
        'AS': 'QUAKING ASPEN'


An example of how to get started is....


        from treetopper import *

        def workflow_1():
            """Workflow 1 will create a quick cruise stand from manually entered trees and plots and will then show a console report.

               Using the ThinTPA class, we will thin the stand to a Trees per Acre of 80 considering all species and diameter ranges
               and then will show a console report of the thinning

               Finally we will export the stand's tree-level data (stand.table_data) to a CSV file in the current working directory"""

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

            print(stand.console_report())

            thin80tpa = ThinTPA(stand, 80)
            print(thin80tpa.console_report())

            stand.table_to_csv('example_csv_export.csv')


        def workflow_2():
            """Workflow 2 will create a full cruise stand from manually entered trees and plots and will then show a console report.

               Using the ThinBA class, we will thin the stand to a BA/ac of 120 considering only DF and WH and all diameter ranges
               and then will show a console report of the thinning

               Finally we will export the stand's tree-level data (stand.table_data) to an Excel file in the current working directory"""

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

            print(stand.console_report())

            thin120ba = ThinBA(stand, 120, species_to_cut=['DF', 'WH'])
            print(thin120ba.console_report())

            stand.table_to_excel('example_xlsx_export.xlsx')


        def workflow_3():
            """Workflow 3 will create a quick cruise stand from importing a stand from a quick cruise Excel file and show a console report.
               The stand class' name needs to match the stand name within the Excel file, we will use "EX4". The Excel file we will be using is
               Example_Excel_quick.xlsx

               Using the ThinRD class, we will thin the stand to a RD/ac of 25 considering only DF and WH with a
               minimum diameter of 10 inches and a max of 18 inches, and then will show a console report of the thinning.

               ** Note this thinning density won't be able to be achieved fully because our parameters don't allow for the needed
               harvest density, but this is to illustrate that the thinning will let the user know how much density was taken and how much
               more is needed to achieve the desired density target"""

            stand = Stand('EX4', -30)
            stand.from_excel_quick('../example_csv_and_xlsx/Example_Excel_quick.xlsx')
            print(stand.console_report())

            thin25rd = ThinRD(stand, 25, species_to_cut=['DF', 'WH'], min_dbh_to_cut=10, max_dbh_to_cut=18)
            print(thin25rd.console_report())


        def workflow_4():
            """Workflow 4 will create a full cruise stand from importing a stand from a full cruise CSV file and show a console report.
               The stand class' name needs to match the stand name within the CSV file, we will use "OK2". The CSV file we will be using is
               Example_CSV_full.csv

               Using the ThinTPA class, we will thin the stand to a TPA of 100 considering all species and diameter ranges
               and then will TRY to show a console report of the thinning.

               ** Note this thinning density is greater than the entire stand's density and the Thin Class will throw a
               TargetDensityError exception which will explain what went wrong"""

            stand = Stand('OK2', 46.94)
            stand.from_csv_full('../example_csv_and_xlsx/Example_CSV_full.csv')

            print(stand.console_report())

            thin100tpa = ThinTPA(stand, 100)
            print(thin100tpa.console_report())

        def workflow_5():
            """Workflow 5 will create a full cruise stand from importing a stand from a full cruise CSV file and export a PDF report.
               The stand class' name needs to match the stand name within the CSV file, we will use "EX3". The CSV file we will be using is
               Example_CSV_quick.csv.

               The PDF will exported to the current working directory as 'stand_report.pdf'

               Using the ThinBA class, we will thin the stand to a BA/ac of 140 considering only DF, WH and RA
               with a maximum thinning DBH of 24 inches (thinning from below). Then a pdf report of the thinning will be exported
               in the current working directory as 'thin_report.pdf'"""

            stand = Stand('EX3', 33.3)
            stand.from_csv_quick('../example_csv_and_xlsx/Example_CSV_quick.csv')
            stand.pdf_report('stand_report.pdf')

            thin140ba = ThinBA(stand, 140, species_to_cut=['DF', 'WH', 'RA'], max_dbh_to_cut=24)
            thin140ba.pdf_report('thin_report.pdf')

        def workflow_6():
            """Workflow 6 will create a full cruise stand from importing a stand from a full cruise Excel file.
               The stand class' name needs to match the stand name within the Excel file, we will use "OK1". The Excel file we will be using is
               Example_Excel_full.csv

               We will then use the FVS class to export the stand's data to three databases in the current working directory.
               These are for use in FVS which is the Forest Service's Forest Vegetation Simulator software

               ** Note the Access Database also needs to have a Suppose.loc file associated with it, this is created as well in
               the same directory as the Access Database"""

            stand = Stand('OK1', -30)
            stand.from_excel_full('../example_csv_and_xlsx/Example_Excel_full.xlsx')

            fvs = FVS()
            fvs.set_stand(stand, 'PN', 612, 6, 45, 'DF', 110)

            fvs.access_db('access_db')
            fvs.sqlite_db('sqlite_db')
            fvs.excel_db('excel_db')


        workflow_1()
        #workflow_2()
        # workflow_3()
        # workflow_4()
        # workflow_5()
        # workflow_6()

		


