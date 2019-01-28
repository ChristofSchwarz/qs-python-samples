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
### Setup on Qlik Sense Server
 * Open QMC of your Sense Server
 * Create a new Analytical Connection with the following settings
 ![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python3.png "screenshot")
 * Import the app "Python Linear Regression.qvf" found in this folder
 * Open this app from the hub
 
## Restart next time
 * Run Command Prompt
```
workon LinearRegression
python ExtensionService_linearRegression.py
```  
