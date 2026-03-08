from flask_restful_swagger import swagger


@swagger.model
class PriceResetRequest:
    def __init__(self, secret):
        self.secret = secret
