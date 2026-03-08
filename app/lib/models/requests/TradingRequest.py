from flask_restful_swagger import swagger


@swagger.model
class TradingRequest:
    def __init__(self, secret, trading_enabled):
        self.secret = secret
        self.trading_enabled = trading_enabled
