ReportGrapher
======

Generating full-fledged report from data.

**Usage**

Folder structure:
	
Data from each month should be put in a folder named
using a YYMM format (e.g. March 2015 would be 1503).
The path to the list of folders containing each month's
data should be put in the config.cfg file. The output 
directory for the .pdf report should also be in the
config file. To generate the report for a specified month,
use:

   > python report.py YYMM
   
The pdf report will be written to the path specified in 
the configuration file with the SecurityWatchReportYYMM.pdf


**report**

Parses data, plots the data using Plotly (bar charts)
and Google Charts (pie charts) then downloads an image
representation of the charts for the report.

**report_csv_monthly**

Parses data from three .csv files to compare statistics 
from different months side-by-side (grouped bar charts).

**gchart**

Instantiates a process to read and serve .html files 
containing graphs plot with the Google Charts API for
Selenium to process and download.

**ltxutils**

Utility class to generate report using latex



**Libraries**

* Flask
* Plotly
* PyVirtualDisplay
* Requests
* Selenium