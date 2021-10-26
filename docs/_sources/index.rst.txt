.. treetopper documentation master file, created by
   sphinx-quickstart on Mon Oct 25 19:50:43 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

treetopper 1.1.1
=================
**Python inventory program from timber stands of the western united states.**

treetopper is a package to run timber stand calculations for timber stands of the western united states. The four main classes that
accomplish this are Stand, Plot, TimberQuick, and TimberFull.

Plots should be made up of the Timber Classes, using the Plot.add_tree() method.
Stands should be made up of Plot Classes, using the Stand.add_plot() method.

Tree and Plot data can be entered manually into the Stand Class...

TimberQuick
~~~~~~~~~~~~

The TimberQuick class takes minimal data (Plot Factor, Species, DBH, Total Height) and will virtually cruise the tree for logs.
Logs will be generated up to the tree's merchantable height, which is calculated as the height at which equals
a diameter of 40% of the tree's diameter at 17 feet (the form height).

If manually creating a Stand with the TimberQuick class, the flow could look like this
::
   from treetopper import Stand, Plot, TimberQuick

   # TimberQuick(Plot Factor, Species, DBH, Total Height, [optional] Preferred Log Length, Minimum Log Length)
   # example_tree = TimberQuick(40, 'DF', 15.5, 87)

   stand = Stand(Stand Name, Plot Factor, [optional] Acres, Inventory Date)

   # List of trees broken out by plot
   tree_list = [
              #Plot1
              [TimberQuick(...), TimberQuick(...), TimberQuick(...), TimberQuick(...)],

              #Plot2
              [TimberQuick(...), TimberQuick(...), TimberQuick(...), TimberQuick(...), TimberQuick(...)]
              ]
   for row in tree_list:
      plot = Plot()
      for tree in row:
          plot.add_tree(tree)
      stand.add_plot(plot)


TimberFull
~~~~~~~~~~~~~~~~~~~~~~~~~~

The TimberFull class can be used if the user has cruised his/her own trees within an inventory. TimberFull still needs the base
params of Plot Factor, Species, DBH and Total Height. And then log data can be added with the add_log() method of TimberFull.
The params for add_log() are Stem Height, Log Length, Log Grade, and Log Defect

If manually creating a Stand with the TimberFull class, the flow could look like this:
::
   from treetopper import Stand, Plot, TimberFull

   # TimberFull(Plot Factor, Species, DBH, Total Height)
   # Log Params within Logs List [Stem Height, Log Length, Log Grade, Log Defect]

   # tree = TimberFull(-25, 'RC', 22.2, 124)
   # log_list = [[42, 40, 'S2', 10], [83, 40, 'S3', 0], [102, 18, 'S4', 15]]

   stand = Stand(...)

   tree_list = [
              #Plot1
              [[TimberFull(...), log_list], [TimberFull(...), log_list], [TimberFull(...), log_list]],

              #Plot2
              [[TimberFull(...), log_list], [TimberFull(...), log_list], [TimberFull(...), log_list]]
              ]
   for row in tree_list:
      plot = Plot()
      for tree, logs in row:
          for log in logs:
              tree.add_log(*log)
          plot.add_tree(tree)
      stand.add_plot(plot)



Import from inventory (.csv, .xlsx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plots and Tree inventories can also be read from CSV and Excel files.

** these files need to be formatted correctly **

To create a formatted blank CSV or Excel inventory sheet, call the blank_sheet module from the terminal and run throught the prompts
::
   python -m treetopper.blank_sheet

Once inventory data is in a correctly formatted sheet, the work flow could look like this:
::
   from treetopper import Stand

   stand = Stand(...)

   # If using a quick cruise sheet
   stand.import_sheet_quick(File Path)

   # If using a full cruise sheet
   stand.import_sheet_full(File Path)



Stand Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once Plots and Trees have been added, two types of reports can be generated: a PDF report or a simple console report, these
reports will display the current stand conditions by species and totals; the log merchantability by grade, log length range,
and species in three categories: logs per acre, board feet per acre and cubic feet per acre; and the stand condition statistics
by species and totals. To generate these reports call either:
::
   stand.pdf_report() #OR
   stand.console_report()



Thinning a Stand
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stands can also be thinned using the Thinning Classes, the three thinning classes are ThinTPA, ThinBA, and ThinRD, they will thin
the stand based on a target Trees per Acre, Basal Area per Acre or Relative Density per Acre, respectively. The user can also
choose only certain species to cut, and minimum and maximum diameter limits. A workflow for this could look like:
::
   from treetopper import Stand, ThinTPA

   stand = Stand(...)
   stand.import_sheet_quick('example_quick_cruise_sheet.xlsx')

   # thin = ThinClass(Stand Class, Target Density, [optional] Species to Cut (list), Minimum DBH to Cut, Maximum DBH to Cut)

   thin80tpa = ThinTPA(stand, 80, species_to_cut=['DF', 'RC', 'WH'], maximum_dbh_to_cut=18)
   thin80tpa.console_report()


Linking to FVS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally if you would like to use the US Forest Service's Forest Vegeation Simulator software, treetopper makes it easy to transfer
stand data to FVS-formatted databases. For more detailed information, view the docs for the FVS class, but a simple example workflow
could look like this:
::
   from treetopper import Stand, FVS

   stand = Stand(...)
   stand.import_sheet_full('example_full_cruise_sheet.xlsx')

   fvs = FVS()

   # fvs.set_stand(Stand Class, FVS Variant Code, FVS Forest Code, FVS Region Code, Stand Age, Site Class Species, Site Index, **kwargs)
   # **kwargs for this method can fill the other columns of a stand database table, to see all columns visit the Forest Service website

   fvs.set_stand(stand, 'PN', 612, 6, 45, 'DF', 110)

   # create a FVS-formatted SQLite Database
   fvs.sqlite_db('example_sqlite_db.db')


Workflow Tutorial and Walk Through
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To walk though six example workflows open the terminal and type
::
   python -m treetopper.stand [workflow number]

[workflow number] should be a number between 1 and 6


**HAPPY CRUISING!**





.. toctree::
   :maxdepth: 4
   :caption: Contents:
    modules




Indices and tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
