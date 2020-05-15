from mongoengine import Document, StringField, EmailField, IntField


class UserDoc(Document):
    username = StringField(required=True, unique=True)
    first_name = StringField()
    last_name = StringField()
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    calories_per_day = IntField(default=2000)
    user_status = IntField(default=["general"])

    meta = {
        'indices': ['username']
    }

    def user_details(self):
        return {'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'password': self.password,
                'calories_per_day': self.calories_per_day,
                'user_status': self.user_status
                }

    # return this when get is called
    def sharable_details(self):
        return {'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'calories_per_day': self.calories_per_day,
                'user_status': self.user_status
                }
