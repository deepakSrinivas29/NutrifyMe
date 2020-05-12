from mongoengine.errors import DoesNotExist
from nutrify.documents.user_doc import UserDoc
from nutrify.documents.meal_doc import MealDoc


def validate_meal_id(meal_id):
    """
    Checks if the meal_id exists
    """
    try:
        meal = MealDoc.objects(meal_id=meal_id).get()
        return meal

    except DoesNotExist:
        return


def validate_user(username):
    """
    :param username:
    :return: UserDoc instance with matching username

    1. Return UserDoc object if username exist in MongoDB.
    2. Else returns 404 response.
    """
    try:
        user = UserDoc.objects(username=username).get()
        return user

    except DoesNotExist:
        return
