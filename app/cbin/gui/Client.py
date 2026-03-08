import json
import requests


class Client:

    def __init__(self, url):
        self._url = url

    def get_product_list(self):
        return self.safe_get('/productList')

    def get_price_history(self, product):
        return self.safe_get('/priceHistory/' + product)

    def get_price(self, product):
        return self.safe_get('/price/' + product)

    def get_trade_history(self):
        return self.safe_get('/tradeHistory')

    def get_order_book(self, product, levels=24):
        return self.safe_get('/orderbook/' + product + '?levels=' + str(levels))

    def get_capitals(self):
        return self.safe_get('/capitals')

    def get_normalized_capital(self):
        return self.safe_get('/normalizedCapitals')

    def trade(self, product, trader_id, qty, side):
        data = {"trader_id": trader_id, "quantity": qty, "side": side}
        return self.safe_post("/trade/" + product, data)

    def safe_get(self, api):
        response = requests.get(self._url + api)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        return {}

    def safe_post(self, api, js=None):
        response = requests.post(self._url + api, json=js)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        return response
