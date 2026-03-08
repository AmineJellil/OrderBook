from lib.util.util import get_time
import threading


class Product:

    def __init__(self, pair, start_price):
        self._pair = pair
        self._priceHistory = {get_time(): start_price}
        self._lock = threading.Lock()

    def next_price(self, price, update_time=None):
        with self._lock:
            self._priceHistory[update_time if update_time is not None else get_time()] = price

    def get_price(self):
        with self._lock:
            last_time = max(self._priceHistory.keys())
            return last_time, self._priceHistory[last_time]

    def get_price_history(self):
        with self._lock:
            return self._priceHistory

    def get_pair(self):
        return self._pair

    def reset_price_history(self, price=None):
        with self._lock:
            if price is not None:
                self._priceHistory = {get_time(): price}
            else:
                self._priceHistory = {get_time(): self._priceHistory[min(self._priceHistory.keys())]}
