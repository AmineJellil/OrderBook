from flask_restful import Resource, marshal_with
from flask_restful_swagger import swagger
from lib.models.results.PriceResult import PriceResult
from ..errors.JsonInvalidErrror import JsonInvalidError
from ..errors.JsonRequiredError import JsonRequiredError


class PriceEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        responseClass=PriceResult.__name__,
        nickname='price',
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
            }
        ])
    @marshal_with(PriceResult.resource_fields)
    def get(self, product):
        """Return a PriceResult object"""

        if not product:
            raise JsonRequiredError()
        try:
            time, price = self.exchange.get_current_price(product=product)
            return PriceResult(time=time, price=price)
        except KeyError:
            raise JsonInvalidError()
