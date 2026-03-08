from lib.models.exchange.Currencies import Currency
from lib.models.exchange.Side import Side

import random
import string
import time


class Trader:

    def __init__(self, user_name, id=None):
        self._user_name = user_name
        if id:
            self._traderId = id
        else:
            self._traderId = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
        self.reset()

    def record_trade(self, trade):
        self._tradeHistory[time.time] = trade
        domestic_inventory = trade.get_quantity() * (1.0 if trade.get_side() is Side.BUY else -1.0)
        foreign_inventory = trade.get_rate() * trade.get_quantity() * (-1.0 if trade.get_side() is Side.BUY else 1.0)
        self._inventory[trade.get_pair().domestic] += domestic_inventory
        self._inventory[trade.get_pair().foreign] += foreign_inventory
        return True

    def get_user_name(self):
        return self._user_name

    def get_trader_id(self):
        return self._traderId

    def get_capital(self, currency):
        return self._inventory[currency]

    def reset(self):
        self._inventory = {currency: 0.0 for currency in Currency}
        self._inventory[Currency.GBP] = 1000000
        self._tradeHistory = {}
