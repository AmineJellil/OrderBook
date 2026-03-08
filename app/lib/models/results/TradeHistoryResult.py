from flask_restful import fields
from flask_restful_swagger import swagger


@swagger.model
class TradeHistoryResult(object):
    """The result of a call to /tradeHistory"""
    resource_fields = {
        'time': fields.Integer,
        'user_name': fields.String,
        'side': fields.String,
        'quantity': fields.Integer,
        'pair': fields.String,
        'rate': fields.Float
    }

    def __init__(self, trade):
        self.time = trade.get_time()
        self.user_name = trade.get_trader().get_user_name()
        self.side = trade.get_side().value
        self.quantity = trade.get_quantity()
        self.pair = trade.get_pair().__str__()
        self.rate = trade.get_rate()
