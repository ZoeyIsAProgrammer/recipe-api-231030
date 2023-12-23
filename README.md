# Recipe App API
Decription of this app:   
In this Recipe API, you can create a user, require a token of the user, using token to get, update, delete user,  
create, list tags and ingredients,  
create, retrieve, list, update, delete recipes, and upload an image to a recipe.

Technologies I used in this project:  
I built this API using **Django REST framework**. In which I have a **custom User model** whose email field is the primary identifier rather than the default username field. For authentication token I use **JWT authentication**. I use **Django's testing framework** to test all functions of this app. I use **flake8** to check the styling issues of this app. I put this app in a **Docker** container, with a **postgres** container as the DB.


## Getting started

To start project, run:

```
docker compose up
```

The API will then be available at [http://127.0.0.1:8001](http://127.0.0.1:8001).

Or for locally running, you can start a venv on top of the requirements.txt file, then run this app with:

```
python manage.py runserver
```