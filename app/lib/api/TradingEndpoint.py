from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger
from lib.models.requests.TradingRequest import TradingRequest

import json

parser = reqparse.RequestParser()
parser.add_argument('secret')
parser.add_argument('trading_enabled')


class TradingEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='trading',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "body",
                "description": "Trading enablement request",
                "required": True,
                "allowMultiple": False,
                "dataType": TradingRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self):
        """Enabling/disabling trading altogether"""

        args = parser.parse_args()
        trading_enabled = args['trading_enabled']
        secret = args['secret']
        success = self.exchange.enable_trading(trading_enabled == 'True') if secret == self.exchange.SECRET else False
        return Response(response=json.dumps({"success": success}),
                        status=200,
                        mimetype="application/json")
