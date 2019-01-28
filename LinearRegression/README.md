 # Linear Regression live-integration with QS
 
 Qlik Sense Server-side Extension to call linear regression from App GUI.
 
 ### 1st time setup
 * Run Command Prompt
 * Setup project environment 
```
mkvirtualenv LinearRegression
```
 * Download/clone this project 
 * Go to the folder where you downloaded/cloned the LinearRegression to
```
cd "C:\Users\admincsw\Documents\GitHub\qs-python-samples\LinearRegression"
setprojectdir .
```
 * install packages (pyparsing, cycler, kiwisolver, python-dateutil, matplotlib, pytz, pandas, mlxtend)
```
pip install grpcio
python -m pip install grpcio-tools
pip install sklearn
pip install numpy
pip install scipy
pip install pandas
``` 
 ### restart next time
 * Run Command Prompt
```
workon LinearRegression
python ExtensionService_linearRegression.py
```  
