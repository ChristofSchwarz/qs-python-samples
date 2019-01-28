# Basket Analysis Server-Side-Extension

This is a python project that acts as a Server-Side Extension for Qlik Sense.

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
pip install grpcio-tools
pip install mlxtend
pip install pandas
```    

### Setup on Qlik Sense Server
 * Open QMC of your Sense Server
 * Create a new Analytical Connection with the following settings
 ![alttext](https://github.com/ChristofSchwarz/pics/raw/master/python4.png "screenshot")
 * Import the app "Python Linear Regression.qvf" found in this folder
 * Open this app from the hub
 
## Restart next time
 * Run Command Prompt
```
workon Basket
python __main__.py
```  
