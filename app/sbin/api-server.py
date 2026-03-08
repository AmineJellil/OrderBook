from flask import Flask
from flask_restful import Api
from flask_restful_swagger import swagger
import pickle
import os

from lib.api.ResetTradersEndpoint import ResetTradersEndpoint
from lib.api.CapitalsEndpoint import CapitalsEndpoint
from lib.api.NormalizedCapitalsEndpoint import NormalizedCapitalsEndpoint
from lib.api.PositionsEndpoint import PositionsEndpoint
from lib.api.PriceEndpoint import PriceEndpoint
from lib.api.PriceResetEndpoint import PriceResetEndpoint
from lib.api.PriceSetterEndpoint import PriceSetterEndpoint
from lib.api.ProductPriceHistoryEndpoint import ProductPriceHistoryEndpoint
from lib.api.ProductsEndpoint import ProductsEndpoint
from lib.api.TradeEndpoint import TradeEndpoint
from lib.api.TradeHistoryEndpoint import TradeHistoryEndpoint
from lib.api.TraderEndpoint import TraderEndpoint
from lib.api.DeleteTraderEndpoint import DeleteTraderEndpoint
from lib.api.TraderQueryEndpoint import TraderQueryEndpoint
from lib.api.TradingEndpoint import TradingEndpoint
from lib.api.OrderBookEndpoint import OrderBookEndpoint
from lib.exchange.Exchange import Exchange
from apscheduler.schedulers.background import BackgroundScheduler

API_VERSION_NUMBER = '1.0'
API_VERSION_LABEL = 'v1'
DATA_PATH = os.getenv("DATA_PATH", "")

def load_exchange():
    with open(os.path.join(DATA_PATH, 'traders.txt'), 'rb') as infile:
        traders = pickle.load(infile)
    with open(os.path.join(DATA_PATH, 'trades.txt'), 'rb') as infile:
        trades = pickle.load(infile)
    return Exchange(traders=traders, trades=trades)


try:
    exchange = load_exchange()
except FileNotFoundError:
    exchange = Exchange()


class FlaskApp(object):

    def __init__(self):
        self.app = Flask(__name__)
        custom_errors = {
            'JsonInvalidError': {
                'status': 500,
                'message': 'JSON format not valid'
            },
            'JsonRequiredError': {
                'status': 400,
                'message': 'JSON input required'
            }
        }

        self.api = swagger.docs(Api(self.app, errors=custom_errors), apiVersion=API_VERSION_NUMBER)

        self.api.add_resource(PriceEndpoint, '/price/<string:product>', endpoint='price',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(TradeEndpoint, '/trade/<string:product>', endpoint='trade',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(ProductPriceHistoryEndpoint, '/priceHistory/<string:product>', endpoint='priceHistory',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(PositionsEndpoint, '/positions/<string:trader_id>', endpoint='positions',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(CapitalsEndpoint, '/capitals', endpoint='currentCapitals',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(NormalizedCapitalsEndpoint, '/normalizedCapitals', endpoint='normalizedCapitals',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(ProductsEndpoint, '/productList', endpoint='existing products',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(TradeHistoryEndpoint, '/tradeHistory', endpoint='tradeHistory',
                              resource_class_kwargs={'exchange': exchange})

        self.api.add_resource(TraderEndpoint, '/trader', endpoint='createTrader',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(ResetTradersEndpoint, '/resetAllTraders', endpoint='resetAllTraders',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(DeleteTraderEndpoint, '/deleteTrader', endpoint='deleteTrader',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(TraderQueryEndpoint, '/traderQuery', endpoint='queryTrader',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(TradingEndpoint, '/enableTrading', endpoint='enableTrading',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(PriceSetterEndpoint, '/priceSetter/<string:product>', endpoint='set price impact',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(PriceResetEndpoint, '/priceReset', endpoint='resetPrice',
                              resource_class_kwargs={'exchange': exchange})
        self.api.add_resource(OrderBookEndpoint, '/orderbook/<string:product>', endpoint='orderbook',
                              resource_class_kwargs={'exchange': exchange})

    def run(self, *args, **kwargs):
        self.app.config['PROPAGATE_EXCEPTIONS'] = False
        self.app.run(*args, **kwargs)


def run_app(*args, **kwargs):
    app = FlaskApp()
    app.run(*args, **kwargs)


def dump_exchange():
    print("Saving exchange")
    pickle.dump(exchange.traders, open(os.path.join(DATA_PATH, 'traders.txt'), 'wb'))
    pickle.dump(exchange.trades, open(os.path.join(DATA_PATH, 'trades.txt'), 'wb'))


if os.getenv("RESET_SCORE_ON_STARTUP") == "true":
    exchange.reset_traders()
    exchange.reset_trade_history()
    dump_exchange()

scheduler = BackgroundScheduler()
job = scheduler.add_job(dump_exchange, 'interval', minutes=1)
scheduler.start()

exchange.start()

if __name__ == '__main__':
    run_app(debug=False, host='0.0.0.0', port=443)
