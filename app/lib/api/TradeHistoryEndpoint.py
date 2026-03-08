from flask_restful import Resource, marshal_with
from flask_restful_swagger import swagger
from lib.models.results.TradeHistoryResult import TradeHistoryResult

from ..errors.JsonInvalidErrror import JsonInvalidError


class TradeHistoryEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='tradeHistory',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ]
    )
    @marshal_with(TradeHistoryResult.resource_fields)
    def get(self):
        """Return all the trades"""

        try:
            trades = self.exchange.get_trade_history()
            return [TradeHistoryResult(t) for t in trades.values()]
        except KeyError:
            raise JsonInvalidError()
