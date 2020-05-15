from flask_restful import Resource
from flask import make_response, request
from mongoengine.errors import DoesNotExist, ValidationError
from nutrify.documents.user_doc import UserDoc
from werkzeug.security import generate_password_hash, check_password_hash
from nutrify.resources.validations import validate_user
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


class Users(Resource):
    """
    This resource is for Creating user and Getting all users.
    """

    @auth.login_required
    def get(self):

        # Returns all users from MongoDB. Add pagination.
        return make_response("Hello This is UserList resource")

    # Creates new user and persists in MongoDB
    def post(self):
        request_body = request.get_json()

        try:
            user = UserDoc.objects(username=request_body['username']).get()
            return make_response("Username not available!", 400)

        except DoesNotExist:
            try:
                user = UserDoc(username=request_body['username'],
                               first_name=request_body['first_name'],
                               last_name=request_body['last_name'],
                               email=request_body['email'],
                               password=generate_password_hash(request_body['password']),
                               calories_per_day=request_body['calories_per_day'],
                               user_status=request_body['user_status']
                               )
                user.save()
                return make_response("Successfully created user!", 200)

            except ValidationError as ex:
                return make_response({'message': ex.message}, 400)


class User(Resource):
    """
    This Resource handles "/users/<string:username>.
    Deals with individual user data.
    """

    @auth.login_required
    def get(self, username):
        """
        Returns User with matching username from authentication header
        """
        if username == auth.username():
            user_data = UserDoc.objects(username=auth.username()).get()
            return make_response(user_data.sharable_details(), 200)

        return make_response("Can't access user.", 401)

    # Update the user with given username as request param
    @auth.login_required
    def put(self, username):

        if username == auth.username():
            user = UserDoc.objects(username=auth.username()).get()
            request_body = request.get_json()

            try:
                user.update(username=request_body['username'],
                            first_name=request_body['first_name'],
                            last_name=request_body['last_name'],
                            email=request_body['email'],
                            password=generate_password_hash(request_body['password']),
                            calories_per_day=request_body['calories_per_day'],
                            user_status=request_body['user_status']
                            )
                user.save()
                return make_response("Successfully updated user!", 201)

            except ValidationError as ex:
                return make_response({'message': ex.message}, 400)

        return make_response("Can't access user.", 401)

    # Delete the user with given username as request param
    @auth.login_required
    def delete(self, username):

        # Get UserDoc object from authentication
        if username == auth.username():
            user = UserDoc.objects(username=auth.username())

            user.delete()
            return make_response("Successfully deleted user!", 200)

        return make_response("Can't access user.", 401)
