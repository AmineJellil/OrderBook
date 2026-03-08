import json

from flask import Response
from flask_restful import Resource
from flask_restful_swagger import swagger

from ..errors.JsonInvalidErrror import JsonInvalidError


class CapitalsEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='positions',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ]
    )
    def get(self):
        """Return the capital of all traders"""

        try:
            capitals = self.exchange.get_capitals()

            result = json.dumps(capitals)
            resp = Response(response=result,
                            status=200,
                            mimetype="application/json")
            return resp
        except KeyError:
            raise JsonInvalidError()
