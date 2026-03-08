from flask import Response
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger


parser = reqparse.RequestParser()
parser.add_argument('levels', type=int, required=False)


class OrderBookEndpoint(Resource):
    def __init__(self, exchange):
        self.exchange = exchange

    @swagger.operation(
        nickname='orderbook',
        responseMessages=[
            {"code": 400, "message": "Invalid product"},
            {"code": 404, "message": "Order book not found"},
        ],
        parameters=[
            {
                "name": "product",
                "description": "Currency pair (e.g. EURGBP)",
                "required": True,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "path"
            }
        ]
    )
    def get(self, product):
        args = parser.parse_args()
        levels = args.get('levels') or 24
        snapshot = self.exchange.get_order_book_snapshot(product_name=product, levels=levels)
        if snapshot is None:
            return Response('Product not found', status=404, mimetype='application/json')
        return snapshot
