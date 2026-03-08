from flask import Response
from flask_restful import reqparse, Resource
from flask_restful_swagger import swagger

from lib.models.requests.TraderQueryRequest import TraderQueryRequest
import json

parser = reqparse.RequestParser()
parser.add_argument('user_name')
parser.add_argument('secret')


class TraderQueryEndpoint(Resource):

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
                "name": "body",
                "description": "Query existing trader",
                "required": True,
                "allowMultiple": False,
                "dataType": TraderQueryRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    def post(self):
        """Queries an existing trader"""

        args = parser.parse_args()
        user_name = args['user_name']
        secret = args['secret']

        trader_id = self.exchange.query_trader(user_name) if secret == self.exchange.SECRET else ''
        result = json.dumps({"trader_id": trader_id})
        resp = Response(response=result,
                        status=200,
                        mimetype="application/json")
        return resp
