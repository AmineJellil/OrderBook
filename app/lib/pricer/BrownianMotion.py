from scipy.stats import norm


class BrownianMotion:

    def __init__(self):
        self._x = 0.0
        self._delta = 0.025
        self._dt = 0.01

    def next_value(self):
        self._x = self._x + norm.rvs(scale=self._delta ** 2 ** self._dt)
        return self._x

    def get_dt(self):
        return self._dt
