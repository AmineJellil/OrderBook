import json

from flask import Response
from flask_restful import Resource
from flask_restful_swagger import swagger

from ..errors.JsonInvalidErrror import JsonInvalidError


class PositionsEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='positions',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "trader_id",
                "description": "trader_id",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path"
            }, ]
    )
    def get(self, trader_id):
        """Return all the known positions"""

        try:
            positions = self.exchange.get_positions(trader_id)
            result = json.dumps(positions)
            resp = Response(response=result,
                            status=200,
                            mimetype="application/json")
            return resp
        except KeyError:
            raise JsonInvalidError()
