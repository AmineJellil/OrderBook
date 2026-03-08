from flask_restful import reqparse, Resource, marshal_with
from flask_restful_swagger import swagger
from lib.models.results.TradeResult import TradeResult
from lib.models.requests.TradeRequest import TradeRequest

parser = reqparse.RequestParser()
parser.add_argument('trader_id', type=str)
parser.add_argument('quantity', type=int)
parser.add_argument('side', type=str)
parser.add_argument('price', type=float)


class TradeEndpoint(Resource):

    def __init__(self, exchange):
        self.exchange = exchange
        self.max_tradesize = 100000

    @swagger.operation(
        responseClass=TradeResult.__name__,
        nickname='trade',
        responseMessages=[
            {"code": 400, "message": "Input required"},
            {"code": 500, "message": "JSON format not valid"},
        ],
        parameters=[
            {
                "name": "product",
                "description": "JSON-encoded name",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path"
            },
            {
                "name": "body",
                "description": "Trade request",
                "required": True,
                "allowMultiple": False,
                "dataType": TradeRequest.__name__,
                "paramType": "body"
            }
        ]

    )
    @marshal_with(TradeResult.resource_fields)
    def post(self, product):
        """Return a TradeResult object"""

        args = parser.parse_args()
        product = product
        trader_id = args['trader_id']
        side = args['side']
        quantity = args['quantity']

        # Disable all trading with quantities below or equal to zero and above max trade size.
        if quantity <= 0 or quantity > self.max_tradesize:
            return TradeResult(success=False, price=0.0)

        (success, price) = self.exchange.try_trade(trader_id=trader_id, side=side,
                                                   qty=quantity, product_name=product)
        return TradeResult(success=success, price=price)
