# AgriMarketWatcher

### Introduction
The AgriMarketWatcher is an initiative within the AgriNeTT project that seeks to provide pricing information of agricultural commodities within Trinidad and Tobago to various stakeholder of the industry. The [AgriNeTT project](http://sta.uwi.edu/agrinett/) is multi-discipline team within the University of the West Indies and other stakeholder that attempt to find ways to use technology to improve the operations of farmers and policy makers within the agricultural industry of Trinidad and Tobago.

The code within this repository is python-based server application that is used to extract the price data for commodities from the [NAMDEVCO's Namis System](http://www.namistt.com/) and the [Trinidad and Tobago Open Data repository](http://data.tt/).

### Features
The server code provides the following features:
* Checks the NAMIS system periodically to determine changes in the prices of the commodities tracked by NAMDEVCO
* Converts the Excel dataset into a simple reusable JSON-based API 



### Dependencies
install libblas-dev liblapack-dev python-dev libatlas-base-dev gfortran libffi-dev libssl-dev

### Installation
virtualenv venv

source venv/bin/activate

pip install -r requirements.txt

using multipack for heroku installatin
https://github.com/Stibbons/heroku-buildpack-libffi