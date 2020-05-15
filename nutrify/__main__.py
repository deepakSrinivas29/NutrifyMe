# using flask_restful

from flask import Flask
from flask_restful import Api
from nutrify.resources.Hello import Hello
from nutrify.resources.Users import Users, User
from nutrify.resources.Meal import Meal
from nutrify.resources.Meals import Meals

from mongoengine import connect

# https://flask-restful.readthedocs.io/en/latest/intermediate-usage.html <-- Reference doc

# creating the flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

api.add_resource(Hello, '/nutrifyme/v1')

api.add_resource(Users, '/nutrifyme/v1/users')
api.add_resource(User, '/nutrifyme/v1/users/<string:username>')

api.add_resource(Meals, '/nutrifyme/v1/meals')
api.add_resource(Meal, '/nutrifyme/v1/meals/<int:meal_id>')

# driver function
if __name__ == '__main__':
    connect('nutrify-me')
    app.run(debug=True)
