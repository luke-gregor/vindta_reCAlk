VINDTA reCAlk
=============
**VINDTA reCALK** is a Python 3.6+ package that recalculates and corrects Dissoled Inorganic Carbon and Total Alkalinity from the Certified Reference Materials run on a VINDTA 3C.


INSTALLATION
------------
This is a flask application that runs from the terminal. To install the app type `pip install vindta_reCAlk`.


USAGE
-----
<img title="screenshot of the app" src="vindta_reCAlk_screenshot_01.png" style="border-style: solid; boder-width: 1px; border-color: #CCC">
The banner at the top of the app will provide instructions for the general usage. Below are the steps.

1. To run the app type `vindta_reCAlk`. This should launch a browser tab that runs from the terminal window. If you close the terminal window, the app will stop.
2. Enter the full path names of the `dbs` file, a folder containing the `dat` titration files. An `xlsx` path also needs to be entered to save the output to. Click on the button to `Create excel from DBS`. The page may not respond for a while - this is just the process running in the background. A textbox will show at the bottom of the page with a log of the processing.
3. Open the Excel file and enter the Silicate, Phosphate, Temperature and Salinity data. Be sure to check that the standard CRM DIC and TA batch values are correct.
4. Enter the name of the Excel file and click on `Recalculate DIC and TA`. The page will be inactive while the process runs in the background (rarely more than 15 seconds). The output will be saved to the excel file. The processing log will also appear in the textbox at the bottom of the page.


ABOUT
-----
- Version: 0.1.8
- Author:  Luke Gregor
- Email:   lukegre@gmail.com
- Date:    2018-08-18

Please acknkowledge this code when you use it.


CHANGE LOG
----------
- **V0.1.8** Fixed `openpyxl` error (can only read `xlsx` and not `xls`)
- **V0.1.7** Python 2 and 3 compatibility issues fixed
- **V0.1.6** added favicons
- **V0.1.5** security update
- **V0.1.4** updated README file.
