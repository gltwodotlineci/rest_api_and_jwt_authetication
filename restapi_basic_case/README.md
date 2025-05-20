# Welcome to this App with Authentication and usage of REST API (RESTful API).
## This application will create and share different API based on relational models.
To start the construction of this application we will need to follow the previews instructions.
First, we start by creating the virtual environment.
``` bash
sudo apt update
sudo apt install python3-venv
# Starting the virtual environment
python3 -m venv env
source ./env/bin/activate
```
Now that we have the virtual environment we can start by adding the application in local.

We can start with downloading the github repository first. Once we have our repository in local. We can add all the dependences by launch the requirements.txt document. document.

# Download repository
``` bash
git clone git@github.com:gltwodotlineci/rest_api_and_jwt_authetication.git
https://github.com/gltwodotlineci/rest_api_and_jwt_authetication.git
# Or if we have the SSH key in the github account:
gti clone https://github.com/gltwodotlineci/rest_api_and_jwt_authetication.git
```
```python
# Now we can add the dependences:
# First, let's enter to the root of the app.
cd rest_api_and_jwt_authetication
python -m pip install -r requirements.txt
# Or
python3 -m pip install -r requirements.txt
```
Checking if the app respects PEP8 practice.

Before we launch the application we will use Flake8 in order to check if the PEP8 practice is respected.

## In the root of the app we can lunch the next commands:
```bash
flake8 restapi_core/urls.py
flake8 restapi_basic_case/urls.py
flake8 restapi_core/permissions.py
flake8 restapi_core/authentication.py
flake8 restapi_core/views.py
flake8 restapi_core/models.py
flake8 restapi_core/serializers.py
# Or
flake8 restapi_basic_case/urls.py restapi_core/urls.py restapi_core/views.py restapi_core/serializers.py restapi_core/models.py restapi_core/permissions.py restapi_core/authentication.py
```
If no mistake is shown, that means that the criteria Pep8 are respected.

Now we can launch our application by using the next command.
```bash
./manage.py runserver
```
