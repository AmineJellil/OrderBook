from apscheduler.schedulers.background import BackgroundScheduler
from lib.pricer.Pricer import Pricer


class PricingEngine:

    def __init__(self, product_universe):
        self._pricers = {product.get_pair(): Pricer(product) for product in product_universe.values()}
        self._scheduler = BackgroundScheduler()

    def start(self):
        for pricer in self._pricers.values():
            self._scheduler.add_job(lambda: pricer.price(), 'interval', seconds=1)
        self._scheduler.start()

    def shutdown(self):
        self._scheduler.shutdown()

    def set_price(self, pair, price):
        self._pricers[pair].price_impact(price)
