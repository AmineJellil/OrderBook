import json

from flask import Response
from flask_restful import Resource
from flask_restful_swagger import swagger


from ..errors.JsonInvalidErrror import JsonInvalidError
from ..errors.JsonRequiredError import JsonRequiredError


class ProductPriceHistoryEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='price',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "product",
                "description": "Product name",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path"
            }
        ])
    def get(self, product):
        """Return a PriceResult object"""

        if not product:
            raise JsonRequiredError()
        try:
            prices = self.exchange.get_product_price_history(product=product)
            result = json.dumps(prices)
            resp = Response(response=result,
                            status=200,
                            mimetype="application/json")
            return resp
        except KeyError:
            raise JsonInvalidError()
