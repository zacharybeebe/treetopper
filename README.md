# treetopper
Python module for calculating Stand data using tree species of the west coast.

DOCUMENTATION
https://zacharybeebe.github.io/treetopper/

## Installation
```bash
pip install treetopper
```


## Blank Inventory Sheet
If you would like to download a blank, formatted inventory sheet in .csv or .xlsx...

```bash
python -m treetopper.blank_sheet
```


## Example Workflows
To go through example workflows with treetopper, this can be done in with the stand module.

There are 6 different workflows that show examples of how treetopper works, these workflows
will show console reports, create csv/xlsx files of stand plot data, create pdf reports,
and/or create FVS-formatted databases

The workflow number (1 through 6) is the only argument when calling the stand module.

```bash
python -m treetopper.stand [workflow_number]
```

The summary of the workflow and the outputs will print at the bottom of the terminal



## Species Available to be cruised
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


## Getting Started
An example of how to get started is...

```python
from treetopper import *

"""
This workflow will create a quick cruise stand from manually entered plot/tree data
and then will display a console report, create a pdf report and create a csv file
of the stand's plot data in the current working directory.

Using the ThinTPA class, we will run a thinning scenario on the stand to a target density
of 80 Trees per Acre considering all species and diameter ranges. Then it will display a
console report of the thinning and create a pdf report.

Finally we will use the FVS class to create a SQLite database that is formatted for use
in FVS. FVS is the US Forest Service's "Forest Vegetation Simulator" software.
"""

## Instantiating the Stand class
stand = Stand('WF1', -20)

"""
Stand(Stand Name, Plot Factor, [optional] Acres, [optional] Inventory Date)
"""

plot_factor = stand.plot_factor

## Entering Tree Data for a Quick Cruise, using the TimberQuick class
tree_data = [
             # Plot 1 trees is the first sub-list
             [TimberQuick('DF', 29.5, 119, plot_factor), TimberQuick('WH', 18.9, 102, plot_factor),
              TimberQuick('WH', 20.2, 101, plot_factor), TimberQuick('WH', 19.9, 100, plot_factor),
              TimberQuick('DF', 20.6, 112, plot_factor)],

             # PLot 2 trees is the second sub-list
             [TimberQuick('DF', 25.0, 117, plot_factor), TimberQuick('DF', 14.3, 105, plot_factor),
              TimberQuick('DF', 20.4, 119, plot_factor), TimberQuick('DF', 16.0, 108, plot_factor),
              TimberQuick('RC', 20.2, 124, plot_factor), TimberQuick('RC', 19.5, 116, plot_factor),
              TimberQuick('RC', 23.4, 121, plot_factor), TimberQuick('DF', 17.8, 116, plot_factor),
              TimberQuick('DF', 22.3, 125, plot_factor)]
             ]
"""
TimberQuick(Species Code, DBH, Total Height, Plot Factor, [optional] Preferred Log Length = 40, [optional] Minimum Log Length = 16)
"""

## Adding Tree data to Plot class and adding the Plot class to the Stand class
for plot_trees in tree_data:
    plot = Plot()
    for tree in plot_trees:
        plot.add_tree(tree)
    stand.add_plot(plot)


## Generating Stand class data reports
stand.console_report()
stand.pdf_report('example_stand_report.pdf')
stand.table_to_csv('example_csv_export.csv')

"""
stand.pdf_report(Filename, [optional] Directory)
stand.table_to_csv(Filename, [optional] Directory)
"""


## Running a thinning scenario on the Stand class, using the ThinTPA class
thin80tpa = ThinTPA(stand, 80)

"""
ThinTPA(Stand Class, Target Density, [optional] Species to Cut (list), [optional] Minimum DBH to Cut, [optional] Maximum DBH to Cut)
"""

## Generating Thin class report
thin80tpa.console_report()
thin80tpa.pdf_report('example_thin_report.pdf')

"""
thin80tpa.pdf_report(Filename, [optional] Directory)
"""


## Creating a FVS-formatted database from the Stand class data
fvs = FVS()
fvs.set_stand(stand, 'PN', 612, 6, 45, 'DF', 110)
fvs.sqlite_db('my_sqlite_fvs.db')

"""
fvs.set_stand(Stand Class, Variant, Forest Number, Region Number, Stand Age, Site Class Species, Site Index, **kwargs)
fvs.sqlite_db(Filename, [optional] Directory, [optional] Blank Database (bool))
"""
```
		


