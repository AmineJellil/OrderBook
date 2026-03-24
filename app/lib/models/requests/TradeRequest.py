from flask_restful_swagger import swagger


@swagger.model
class TradeRequest:
    def __init__(self, trader_id, quantity, side, price=None):
        self.trader_id = trader_id
        self.quantity = quantity
        self.side = side
        self.price = price
