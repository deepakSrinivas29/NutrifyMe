from flask_restful import Resource
from flask import jsonify, make_response, request
from werkzeug.security import check_password_hash

from nutrify.utils import fetch_calories
from mongoengine.errors import DoesNotExist, ValidationError
from nutrify.documents.user_doc import UserDoc
from nutrify.documents.meal_doc import MealDoc
from nutrify.resources.validations import validate_user, validate_meal_id
from datetime import datetime
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    try:
        user = UserDoc.objects(username=username).get()
        if not check_password_hash(user.password, password):
            return make_response("Invalid Password - Authentication failed!", 404)

        return username

    except DoesNotExist:
        return make_response("Authentication failed!", 404)


class UserMeal(Resource):

    # To get meal with matching meal_id of a given username
    @auth.login_required
    def get(self, username, meal_id):
        user = validate_user(username)

        if not user:
            return make_response("User not found!", 404)

        meal = validate_meal_id(meal_id)

        if meal:
            meal_data = meal.json_format()
            return make_response(meal_data, 200)

        return make_response("Meal not found!", 404)

    # To delete meal with matching meal_id of a given username
    @auth.login_required
    def delete(self, username, meal_id):
        user = validate_user(username)  # contains user else none

        if not user:
            return make_response("User not found!", 404)

        meal = validate_meal_id(meal_id)  # contains meal else none

        if meal:
            meal.delete()
            return make_response('Successfully deleted meal!', 200)

        return make_response("Meal not found!", 404)

    # To update meal with matching meal_id of a given username
    @auth.login_required
    def put(self, username, meal_id):

        global current_meal_calories

        request_body = request.get_json()
        current_user = validate_user(username)  # contains user else none

        if not current_user:
            return make_response("User not found!", 404)

        meal = validate_meal_id(meal_id)  # contains meal else none

        if meal:
            # Get Calorie information from Nutritionix
            # current_meal_calories = 0

            try:
                if 'calories' not in request_body or not request_body['calories']:
                    current_meal_calories = int(fetch_calories(request_body['food_name']))

            except Exception as ex:
                print('Could not reach Nutritionix to get data' + str(ex))
                current_meal_calories = 0

            # Calories of all meal except the meal being updated. To update is_in_days_limit
            calories_consumed_today = MealDoc.objects(username=current_user.username,
                                                      meal_id__ne=meal_id,
                                                      date__gte=datetime.now().date()).as_pymongo().sum('calories')

            if calories_consumed_today + current_meal_calories > current_user.calories_per_day:
                meal.is_in_days_limit = False

            meal.update(meal_id=request_body['meal_id'],
                        food_name=request_body['food_name'],
                        username=request_body['username'],
                        description=request_body['description'],
                        calories=current_meal_calories
                        )
            meal.date = datetime.now()
            meal.save()
            return make_response('Successfully deleted meal!', 200)

        return make_response("Meal not found!", 404)
