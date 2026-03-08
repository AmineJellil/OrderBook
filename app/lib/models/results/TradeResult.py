from flask_restful import fields
from flask_restful_swagger import swagger


@swagger.model
class TradeResult(object):
    """The result of a call to /trade"""
    resource_fields = {
        'price': fields.String,
        'success': fields.Boolean
    }

    def __init__(self, price, success):
        self.price = price
        self.success = success
