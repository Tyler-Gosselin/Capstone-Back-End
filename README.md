# Summary

> This project was made while attending the Bottega Coding bootcamp. The project is built using a Flask API using a SQL database. The front end was built with React. 

## Dependency Docs

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Flask Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/)
- [Marshmallow-sqlalchemy](https://marshmallow-sqlalchemy.readthedocs.io/en/latest/)
- [flask-cors](https://flask-cors.readthedocs.io/en/latest/)
- [venv](https://docs.python.org/3/tutorial/venv.html)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

# How to start / Install

## Starting the server

- Run the following commands in the terminal while in the 'backend' folder

  - This will create a venv folder. If you would like the folder to be named differently change the second 'venv' in the command.

  ```
  $ python -m venv venv
  ```

- To activate the virtual environment use the command

  ```
  $ venv\Scripts\activate (for Windows)
  $ source venv/bin/activate (for Mac)
  ```

  - You will see in your terminal that your location will look like :
    ```
    (venv) your directory here
    ```

## Installing packages

- To begin installing packages use the command :

```
$ pip install package-name
```

- If you need to regenerate your environment, you can create a requirements.txt file in the root folder of your project. Use this command to produce this list

```
$ pip freeze > requirements.txt
```

- To recreate this list on a different machine use the command:

```
$ pip install -r requirements.txt
```

## Database Setup

- To set up a database, inside a python repl used the commands:

```
>>> from yourFileNameHere import db
>>> db.create_all()
```

# Routes

### Get all users

- localhost:5000/api/get-users

### Get all blogs

-localhost:5000/api/get-blogs

### Get single user

-localhost:5000/api/get-users

### Get single blog

-localhost:5000/api/get-blog/<id>

### Create a user

-localhost:5000/api/register-user

```json
body: {
	"username": "",
	"email": "",
  "password": ""
}
```

### Create a blog

-localhost:5000/api/create-blog

```json
body: {
	"title": "",
	"content": ""
}
```

### Edit a blog

-localhost:5000/api/edit-blog/<id>

### Login

-localhost:5000/api/login

```json
body: {
	"username": "",
	"email": "",
  "password": ""
}
```

### Logout

-localhost:5000/api/logout

### Delete User

-localhost:5000/api/delete-user/<id>

### Delete a blog

-localhost:5000/api/delete-blog/<id>
