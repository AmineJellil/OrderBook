from flask_restful_swagger import swagger


@swagger.model
class PriceSetRequest:
    def __init__(self, secret, price):
        self.secret = secret
        self.price = price
