from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger
from lib.models.requests.PriceSetRequest import PriceSetRequest

import json

parser = reqparse.RequestParser()
parser.add_argument('secret')
parser.add_argument('price')


class PriceSetterEndpoint(Resource):

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
                "name": "product",
                "description": "JSON-encoded name",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path"
            },
            {
                "name": "body",
                "description": "Price set request",
                "required": True,
                "allowMultiple": False,
                "dataType": PriceSetRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self, product):
        """Price fixing 101 """

        args = parser.parse_args()
        price = args['price']
        secret = args['secret']
        success = self.exchange.set_price(product, price) if secret == self.exchange.SECRET else False
        result = json.dumps({"success": success})
        resp = Response(response=result,
                        status=200,
                        mimetype="application/json")

        return resp
