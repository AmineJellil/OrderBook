from collections import deque
from lib.pricer.BrownianMotion import BrownianMotion
from math import exp
from scipy.stats import norm
import threading


class Pricer:

    def __init__(self, product):
        self._product = product
        self._next_prices = deque()
        self._brownian_motion = BrownianMotion()
        self._initial_price = product.get_price()[1]
        self._domestic_ir = 0.0005
        self._foreign_ir = 0.003
        self._volatility = 0.05
        self._time = 1
        self._lock = threading.Lock()

    def price(self):
        with self._lock:
            if self._next_prices:
                self._time = self._time + self._brownian_motion.get_dt()
                self._product.next_price(self._next_prices.popleft())
            else:
                self.next_price()

    def next_price(self):
        p0 = self._initial_price
        rb = self._foreign_ir
        ra = self._domestic_ir
        t = self._time
        sigma = self._volatility
        wt = self._brownian_motion.next_value()
        self._product.next_price(p0 * exp((rb - ra) * t - sigma ** 2 * t / 2 + sigma * wt))
        self._time = self._time + self._brownian_motion.get_dt()

    def price_impact(self, price, impact_period=60, recovery_period=300, volatility=0.005):
        current_price = self._product.get_price()[1]
        with self._lock:
            for i in range(impact_period):
                linear_price = current_price + i * (price - current_price) / impact_period
                self._next_prices.append(linear_price * norm.rvs(loc=1, scale=volatility))
            for i in range(recovery_period):
                linear_price = price + i * (current_price - price) / recovery_period
                self._next_prices.append(linear_price * norm.rvs(loc=1, scale=volatility))
