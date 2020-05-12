# using flask_restful

from flask import Flask
from flask_restful import Api
from nutrify.resources.Hello import Hello
from nutrify.resources.Users import UserList, User
from nutrify.resources.UserMeal import UserMeal
from nutrify.resources.Meals import Meals

from mongoengine import connect

# https://flask-restful.readthedocs.io/en/latest/intermediate-usage.html <-- Reference doc

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

api.add_resource(Hello, '/')
api.add_resource(UserList, '/users', endpoint='users')
api.add_resource(User, '/users/<string:username>', endpoint='user')
api.add_resource(UserMeal, '/users/<string:username>/<int:meal_id>', endpoint='user_meal_id')
api.add_resource(Meals, '/meals', endpoint='meals')
api.add_resource(Meals, '/meals/<string:username>', endpoint='meal_username')

# driver function
if __name__ == '__main__':
    connect('nutrify-me')
    app.run(debug=True)
