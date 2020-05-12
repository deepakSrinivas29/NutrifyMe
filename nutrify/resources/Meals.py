from flask_restful import Resource
from flask import jsonify, make_response, request
from nutrify.utils import fetch_calories
from mongoengine.errors import DoesNotExist, ValidationError
from nutrify.documents.user_doc import UserDoc
from nutrify.documents.meal_doc import MealDoc
from nutrify.resources.validations import validate_user, validate_meal_id
from werkzeug.security import check_password_hash
from datetime import datetime
import uuid
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = validate_user(username)

    if user:
        if not check_password_hash(user.password, password):
            return make_response("Invalid Password - Authentication failed!", 404)

        return username

    return make_response("Invalid Username - Authentication failed!", 404)


class Meals(Resource):

    @auth.login_required
    def get(self, username):

        # if username matches return all meals of the user
        if validate_user(username) is not None:
            meals_list = MealDoc.objects(username=username).all()

            # converts each object in query set to dict and hold them in a list
            meals_json = [meal.json_format() for meal in meals_list]

            return make_response(jsonify(meals_json), 200)

        return make_response("User not found!", 404)

    # Creates new meal for a user
    def post(self):

        global current_meal_calories
        request_body = request.get_json()

        # request_body["meal_id"] = str(uuid.uuid4())

        # Current user from request body and validate it.
        current_user = validate_user(request_body['username'])

        if current_user is None:
            return make_response("User not found!", 404)

        # If meal_id is not previously assigned to a Meal.
        if validate_meal_id(request_body['meal_id']) is None:

            # Get Calorie information from Nutritionix
            # current_meal_calories = 0

            try:
                if 'calories' not in request_body or not request_body['calories']:
                    current_meal_calories = int(fetch_calories(request_body['food_name']))

            except Exception as ex:
                print('Could not reach Nutritionix to get data' + str(ex))
                current_meal_calories = 0

            # Add meal to MealDoc
            try:
                meal = MealDoc(meal_id=request_body['meal_id'],
                               food_name=request_body['food_name'],
                               username=request_body['username'],
                               description=request_body['description'],
                               calories=current_meal_calories,
                               )

                # Update is_in_days_limit flag
                # returns sum of calories of all meals created today of matching username
                calories_consumed_today = MealDoc.objects(username=current_user.username,
                                                          date__gte=datetime.now().date()).as_pymongo().sum('calories')

                if calories_consumed_today + current_meal_calories > current_user.calories_per_day:
                    meal.is_in_days_limit = False

                meal.date = datetime.now()
                meal.save()

                return make_response("Successfully created Meal!", 200)

            except ValidationError as ex:
                return make_response({'message': ex.message}, 400)

        return make_response("Change Meal_ID!", 400)
