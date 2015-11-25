ReportGrapher
======

Generating full-fledged report from data.

Project during internship at HKCERT.

**Usage**

Folder structure:

The top directory should contain:

* report_monthly.py
* report_quarterly.py
* report_gchart.py
* report_utils.py
* gchart.html
* config.cfg

The output folders for the LaTeX PDF Security Watch Report and
the PNG files of the charts should be in the configuration 
file config.cfg as a **relative** path.


**Monthly Report**	

Data from each month should be put in a folder named
using a YYMM format (e.g. March 2015 would be 1503).
The path to the list of folders containing each month's
data should be put in the config.cfg file under the 
[monthly] section under **input**

To generate the report for a specified month,
use:

```
   > python report_monthly.py YYMM
```
   
The pdf report will be written to the folder specified in 
the configuration file under [monthly] with the name 
SecurityWatchReportYYMM.pdf


**Quarterly Report**	

Data from each month should be put in a folder named
using a YYQQ format (e.g. 2014 Q3 would be 1403).
The path to the list of folders containing each month's
data should be put in the config.cfg file under the 
[quarterly] section under **input**.

To generate the report for a specified quarter, 
use:


```
   > python report_quarterly.py YYQQ
```


The pdf report will be written to the folder specified in 
the configuration file under [quarterly] with the name 
SecurityWatchReportYYYYQQ.pdf


Scripts
======


**report_monthly**

Parses data from csv files to generate the monthly report.

**report_quarterly**

Parses data from csv files to generate the quarterly report.

**report_utils**

Utility functions:

* Reads from csv files 
* Plots bar/line graphs using Plotly API
* Downloads graphs from Plotly using *requests*
* Starts a thread to handle the *report_gchart* so that the main thread is not blocked
* Prints to console without newline
* Sums arrays by index

**report_gchart**

Instantiates a process to read and serve .html files 
containing graphs plot with the Google Charts API for
Selenium to process and download.

**ltxutils**

Utility class to generate report using latex



External Libraries
======

* Flask
* Plotly
* PyVirtualDisplay
* Requests
* Selenium
