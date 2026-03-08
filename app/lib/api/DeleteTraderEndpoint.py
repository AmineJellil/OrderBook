from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger

from lib.models.requests.TraderRequest import TraderRequest
import json

parser = reqparse.RequestParser()
parser.add_argument('user_name')
parser.add_argument('secret')


class DeleteTraderEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='deleteTrader',
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
    def delete(self):
        """Deletes a new trader"""

        args = parser.parse_args()
        user_name = args['user_name']
        secret = args['secret']

        # If the secret is invalid, return early
        if secret != self.exchange.SECRET:
            result = json.dumps({"error": "Invalid secret"})
            resp = Response(response=result,
                            status=401,
                            mimetype="application/json")
            return resp
        
        # If the secret is valid, delete the trader

        trader_id = self.exchange.delete_trader(user_name)
        result = json.dumps({"trader_id": trader_id})
        resp = Response(response=result,
                        status=200,
                        mimetype="application/json")
        return resp
