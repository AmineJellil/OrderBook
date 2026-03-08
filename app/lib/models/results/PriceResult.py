from flask_restful import fields
from flask_restful_swagger import swagger


@swagger.model
class PriceResult(object):
    """The result of a call to /price"""
    resource_fields = {
        'time': fields.Integer,
        'price': fields.Float
    }

    def __init__(self, time, price):
        self.time = time
        self.price = price
