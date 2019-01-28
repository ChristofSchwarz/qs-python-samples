 # Linear Regression live-integration with QS
 
 Qlik Sense Server-side Extension to call linear regression from App GUI.
 
 ## 1st time setup
 * Run Command Prompt
 * Download/clone this project 
 * Go to the folder where you downloaded/cloned the LinearRegression to and also create a environment with the same name
```
cd "C:\Users\admincsw\Documents\GitHub\qs-python-samples\LinearRegression"
mkvirtualenv LinearRegression
setprojectdir .
```
 * install Python packages 
```
pip install grpcio
python -m pip install grpcio-tools
pip install sklearn
pip install pandas
``` 
 * Run the Python app
```
python ExtensionService_linearRegression.py
```
### Setup on Qlik Sense Desktop
 * Edit Settings.ini file found under your Documents\Qlik\Sense e.g. C:\Users\csw\Documents\Qlik\Sense\Settings.ini
 * If there is no such section \[Settings 7\] create it and add the entry for "SSEPlugin="
```
[Settings 7]
SSEPlugin=PythonRegression,localhost:50059
```
 * if there is already another SSE plugin, add this using a ; to separate multiple entries, e.g.
```
[Settings 7]
SSEPlugin=PythonBasket,localhost:50088;PythonRegression,localhost:50059
``` 
 * Copy the app "Python Basket Analysis AAI.qvf" from this project folder into Documents\Qlik\Sense\Apps e.g. C:\Users\csw\Documents\Qlik\Sense\Apps
 * Run or restart Qlik Sense Desktop and log in
 * Open app "Python Linear Regression" from the hub and see the trend line on first sheet
![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python8.png "screenshot")

### Setup on Qlik Sense Server
 * Open QMC of your Sense Server
 * Create a new Analytical Connection with the following settings
 ![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python3.png "screenshot")
 * Import the app "Python Linear Regression.qvf" found in this folder
 * Open app "Python Linear Regression" from the hub and see the trend line on first sheet
 
## Restart next time
 * Run Command Prompt
```
workon LinearRegression
python ExtensionService_linearRegression.py
```  
