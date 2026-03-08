import datetime


class Plotter:

    def __init__(self, client):
        self._client = client
        self._product_universe = self._client.get_product_list()
        self._x = {}
        self._y = {}
        self.init_plot()

    def init_plot(self):
        for p in self._product_universe:
            data = self._client.get_price_history(p)
            self._x[p] = [datetime.datetime.utcfromtimestamp(int(t)) for t in data.keys()]
            self._y[p] = [float(r) for r in data.values()]

    def update_plot(self):
        for p in self._product_universe:
            data = self._client.get_price(p)
            self._x[p].append(datetime.datetime.utcfromtimestamp(int(data['time'])))
            self._y[p].append(float(data['price']))

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y
