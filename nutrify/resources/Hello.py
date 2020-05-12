from flask_restful import Resource
from flask import jsonify


class Hello(Resource):

    def get(self):
        return jsonify({'message': 'hello world'})