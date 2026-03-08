class Trade:
    def __init__(self, trader, side, qty, pair, rate, time):
        self._trader = trader
        self._side = side
        self._qty = qty
        self._pair = pair
        self._rate = rate
        self._time = time

    def get_variation(self):
        if self._side == 'Buy':
            return self._qty
        else:
            return -self._qty

    def get_trader(self):
        return self._trader

    def get_pair(self):
        return self._pair

    def get_quantity(self):
        return self._qty

    def get_side(self):
        return self._side

    def get_time(self):
        return self._time

    def get_rate(self):
        return self._rate
