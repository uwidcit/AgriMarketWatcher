# AgriMarketWatcher
A service to receive price information from NAMDEVCO

### Introduction

The AgriMarketWatcher is an initiative within the AgriNeTT project that seeks to provide pricing information of 
agricultural commodities within Trinidad and Tobago to various stakeholder of the industry. 
The [AgriNeTT project](http://sta.uwi.edu/agrinett/) is multi-discipline team within the 
University of the West Indies and other stakeholder that attempt to find ways to use technology to 
improve the operations of farmers and policy makers within the agricultural industry of Trinidad and Tobago.

The code within this repository is python-based server application that is used to extract the price data for 
commodities from the [NAMDEVCO's Namis System](http://www.namistt.com/) and 
the [Trinidad and Tobago Open Data repository](http://data.tt/).

### Features

The server code provides the following features:
* Checks the NAMIS system periodically to determine changes in the prices of the commodities tracked by NAMDEVCO
* Converts the Excel dataset into a simple reusable JSON-based API 


### Dependencies
* Runs on Python 3.9
* Listed in the requirements.txt file

### Installation

```bash
virtualenv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```


using multipack for heroku installatin
https://github.com/Stibbons/heroku-buildpack-libffi


### Database Upgrade

```bash
heroku run python manage.py db upgrade --app agrimarketwatch
```


## Development Notes
### Development Environment
1. We recommend a linux/unix environment. If using windows, the Linux Subsystem might be better than powershell or cmd
2. Install Git for your platform
3. [Generate an SSH Key ](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)and [Add you machine SSH key to your github profile](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account). (we recommend using git over https for authenticating Git repo)
4. Install [pyenv](https://github.com/pyenv/pyenv) to manage python enviornment
5. Install poetry
6. Install Visual Studio Code
7. Adding the Visual Studio Code python plugin


If using a mac, we recommend installing poetry with pipx
https://pypa.github.io/pipx/installation/

### Connecting to Heroku
1. [Clone the Repo](https://github.com/uwidcit/AgriMarketWatcher)
2. [Install the Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Install the [Heroku Repo Plugin](https://github.com/heroku/heroku-repo)
   ```bash
   heroku plugins:install heroku-repo
   ```
4. Log-in to Heroku 
   ```bash
   heroku login
   ```
5. Verify you can view the app from the CLI
   ```bash
   heroku config --app agrimarketwatch
   ```
6. Connect remote deployment with the URI
   ```bash
   heroku git:remote --app agrimarketwatch
   ```
7. Verify remote added succesfully (should see a `heroku` and `origin` remote listing)
   ```bash
   git remote -v
   ```

### Setup the python environment
1. Use pyenv to setup an environment matching python version in `runtime.txt` and is a [supported runtime in Heroku](https://devcenter.heroku.com/articles/python-support#supported-runtimes)
   ```bash
   pyenv install 3.9.16
   pyenv local 3.9.16  # Activate Python 3.9 for the current project
   poetry env use -- $(which python)
   poetry install
   ```
2. Ensure to use the `pyenv local 3.9.16` before starting development in each 


### Running the dev environment
Run redis in the background
```bash
docker run --name redis-dev -p 6379:6379 -d redis
```