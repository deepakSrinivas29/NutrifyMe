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
    # Return UserDoc if username matches else None
    user = validate_user(username)

    if user is not None:
        if not check_password_hash(user.password, password):
            return make_response("Invalid Password - Authentication failed!", 404)

    return make_response("Authentication failed!", 404)


class Meal(Resource):

    # To get meal with matching meal_id of a given username
    @auth.login_required
    def get(self, meal_id):
        # Return MealDoc if meal_id exists else None
        meal = validate_meal_id(meal_id)

        if not meal:
            return make_response("Meal not found!", 404)

        if meal.username != auth.username():
            return make_response("Can't access the meal.", 401)

        meal_data = meal.json_format()
        return make_response(meal_data, 200)

    # To delete meal with matching meal_id of a given username
    @auth.login_required
    def delete(self, meal_id):
        # Return MealDoc if meal_id exists else None
        meal = validate_meal_id(meal_id)

        if not meal:
            return make_response("Meal not found!", 404)

        if meal.username != auth.username():
            return make_response("Can't access the meal.", 401)

        meal.delete()
        return make_response('Successfully deleted meal!', 200)

    # To update meal with matching meal_id of a given username
    @auth.login_required
    def put(self, meal_id):

        global current_meal_calories

        # Return MealDoc if meal_id exists else None
        meal = validate_meal_id(meal_id)

        if not meal:
            return make_response("Meal not found!", 404)

        request_body = request.get_json()
        current_user = UserDoc.objects(username=auth.username()).get()

        # Get Calorie information from Nutritionix
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
