from mongoengine import Document, StringField, EmailField, IntField, DateTimeField, BooleanField
from datetime import datetime


class MealDoc(Document):
    meal_id = IntField(required=True, unique=True)
    food_name = StringField(required=True)
    description = StringField(default="--NA--")
    calories = IntField(default=0)
    date = DateTimeField(required=True)
    username = StringField(required=True)
    is_in_days_limit = BooleanField(default=True)

    meta = {
        'indexes': ['username', 'meal_id']
    }

    def json_format(self):
        return {'meal_id': self.meal_id,
                'food_name': self.food_name,
                'username': self.username,
                'description': self.description,
                'date': self.date,
                'calories': self.calories,
                'is_in_days_limit': self.is_in_days_limit
                }

