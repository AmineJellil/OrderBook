from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger

from lib.models.requests.TraderRequest import TraderRequest
import json

parser = reqparse.RequestParser()
parser.add_argument('user_name')
parser.add_argument('secret')
parser.add_argument('id')


class TraderEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='trader',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "body",
                "description": "Trader request",
                "required": True,
                "allowMultiple": False,
                "dataType": TraderRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self):
        """Creates a new trader"""
        args = parser.parse_args()
        user_name = args['user_name']
        secret = args['secret']

        try:
            trader_id = args['id']
        except Exception:
            trader_id = None

        # If the secret is invalid, return early
        if secret != self.exchange.SECRET:
            result = json.dumps({"error": "Invalid secret"})
            resp = Response(response=result,
                            status=401,
                            mimetype="application/json")

        # If the secret is valid, create a new traderID, if username
        # matches an existing one, this will be overriden.

        trader_id = self.exchange.create_trader(user_name, trader_id)
        result = json.dumps({"trader_id": trader_id})
        resp = Response(response=result,
                        status=200,
                        mimetype="application/json")
        return resp
