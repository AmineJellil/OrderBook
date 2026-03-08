from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger
from lib.models.requests.SecretOnlyRequest import SecretOnlyRequest

import json

parser = reqparse.RequestParser()
parser.add_argument('secret')


class PriceResetEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='pricing',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "body",
                "description": "Prices reset request",
                "required": True,
                "allowMultiple": False,
                "dataType": SecretOnlyRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self):
        """Resetting all price history to initial values """

        args = parser.parse_args()
        secret = args['secret']
        success = self.exchange.reset_prices() if secret == self.exchange.SECRET else False
        result = json.dumps({"success": success})
        resp = Response(response=result,
                        status=200,
                        mimetype="application/json")

        return resp
