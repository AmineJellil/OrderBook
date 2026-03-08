import json

from flask import Response
from flask_restful import Resource
from flask_restful_swagger import swagger

from ..errors.JsonInvalidErrror import JsonInvalidError


class ProductsEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='products',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ]
    )
    def get(self):
        """Return the available products"""

        try:
            products = self.exchange.get_products()

            result = json.dumps(products)
            resp = Response(response=result,
                            status=200,
                            mimetype="application/json")
            return resp
        except KeyError:
            raise JsonInvalidError()
