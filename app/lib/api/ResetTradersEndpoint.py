from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger


import json

from lib.models.requests.SecretOnlyRequest import SecretOnlyRequest

parser = reqparse.RequestParser()
parser.add_argument('secret')

class ResetTradersEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='reset_traders',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "body",
                "description": "Reset all traders portfolio and positions",
                "required": True,
                "allowMultiple": False,
                "dataType": SecretOnlyRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self):
        """Reset all traders"""
        args = parser.parse_args()
        secret = args['secret']

        # If the secret is invalid, return early
        if secret != self.exchange.SECRET:
            result = json.dumps({"error": "Invalid secret"})
            resp = Response(response=result,
                            status=401,
                            mimetype="application/json")

        # If the secret is valid, reset all traders
        self.exchange.reset_traders()
        self.exchange.reset_trade_history()
        return Response(status=200)
