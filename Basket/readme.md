# Basket Analysis Server-Side-Extension

This is a python project that acts as a Server-Side Extension for Qlik Sense. The python code was developed by <a href="https://github.com/rileymd88">Riley MD</a>, thanks for the genious work.

If you've already set up this example and re-run it, go to <a href="#restart-next-time">Restart</a>

## 1st time setup
 * Run Command Prompt
 * Download/clone this project 
 * Go to the folder where you downloaded/cloned the LinearRegression to and also create a environment with the same name
```
cd "C:\Users\admincsw\Documents\GitHub\qs-python-samples\Basket"
mkvirtualenv Basket
setprojectdir .
```
![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python7.png "screenshot")

 * install Python packages 
```
pip install grpcio
pip install grpcio-tools
pip install mlxtend
pip install pandas
```    
 * Run the Python app
```
python __main__.py
```
### Setup on Qlik Sense Desktop
 * Edit Settings.ini file found under your Documents\Qlik\Sense e.g. C:\Users\csw\Documents\Qlik\Sense\Settings.ini
 * If there is no such section "Settings 7" create it and add the entry for "SSEPlugin="
```
[Settings 7]
SSEPlugin=PythonBasket,localhost:50088
```
 * if there is already another SSE plugin, add this using a ; to separate multiple entries, e.g.
```
[Settings 7]
SSEPlugin=PythonRegression,localhost:50059;PythonBasket,localhost:50088
``` 
 * Copy the app "Python Basket Analysis AAI.qvf" from this project folder into Documents\Qlik\Sense\Apps e.g. C:\Users\csw\Documents\Qlik\Sense\Apps
 * Run or restart Qlik Sense Desktop and log in
 * Find the Data connection "PythonBasketSampleQVDs" on the right and click the pen icon (edit)
![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python5.png "screenshot") 
 * change this (invalid) path to where the qvd files are located, they are in a subfolder of this project
* Reload the app (this is where the integration happens, the Qlik load script submits data to Python and waits for the response)

### Setup on Qlik Sense Server
 * Open QMC of your Sense Server
 * Create a new Analytical Connection with the following settings
 ![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python4.png "screenshot")
 * Import the app "Python Basket Analysis AAI.qvf" found in this folder
![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python6.png "screenshot") 
 * Open this app from the hub
 * Go to DataloadEditor (Load Script)
 * Find the Data connection "PythonBasketSampleQVDs" on the right and click the pen icon (edit)
![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python5.png "screenshot") 
 * change this (invalid) path to where the qvd files are located, they are in a subfolder of this project
 * Since the connection automatically gets renamed and "(machine_user)" gets added to the connection name, please adjust the variable vLib in row 21 accordingly, e.g.
```
SET vLib = 'lib://PythonBasketSampleQVDs (qse-csw_admincsw)\';
```
 * Reload the app (this is where the integration happens, the Qlik load script submits data to Python and waits for the response)
 
## Restart next time
 * Run Command Prompt
```(python)
workon Basket
python __main__.py
```  
