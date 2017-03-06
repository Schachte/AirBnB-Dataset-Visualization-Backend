##Airbnb Data Visualization Backend
###Dependency Management
- Installing virtual environment to manage local dependencies `pip install virtualenv'
- Make a virtualenv in your directory by typing `virtualenv venv`
- To activate the virtualenv, type in `source venv/bin/activate`
- Install all the requirements from the requirements.txt file from `pip install -r requirements.txt`

###Setting Up Django Related Elements
- First, sync the database `python manage.py migrate` (Make sure you're in the directory that manage.py is contained in)
- Create a superuser that you can test admin priveleges on `python manage.py createsuperuser`

###Running the Server
`python manage.py runserver`

- 
