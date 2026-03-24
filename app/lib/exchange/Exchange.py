from lib.models.exchange.Currencies import UNIVERSE, EURGBP, get_pair, Currency
from lib.models.exchange.Product import Product
from lib.models.exchange.Side import Side, get_side
from lib.models.exchange.Trade import Trade
from lib.models.exchange.Trader import Trader
from lib.pricer.PricingEngine import PricingEngine
from lib.exchange.OrderBook import OrderBook
from lib.exchange.NPCManager import NPCManager
import sys
import os

class Exchange:
    PRODUCT_UNIVERSE = {
        EURGBP: Product(EURGBP, 0.87),
    }

    NORMALIZING_CURRENCY = Currency.GBP

    SECRET = os.getenv('SECRET', 'Hackathon19')

    def __init__(self, traders=None, trades=None):
        if trades is None:
            trades = []
        if traders is None:
            traders = {}
        self.traders = traders
        self.trades = trades
        self.pricing_engine = PricingEngine(self.PRODUCT_UNIVERSE)
        self.order_books = {str(pair): OrderBook(str(pair)) for pair in self.PRODUCT_UNIVERSE}
        self.npc_managers = {symbol: NPCManager(book) for symbol, book in self.order_books.items()}
        self.trading_enabled = True

    def start(self):
        self.pricing_engine.start()

    def shutdown(self):
        self.pricing_engine.shutdown()

    def set_price(self, product, price):
        """Having passed the secret check, product is freeform text and price is possibly text too"""
        self.pricing_engine.set_price(get_pair(product), float(price))
        return True

    def reset_prices(self):
        self.pricing_engine.shutdown()
        for product in self.PRODUCT_UNIVERSE.values():
            product.reset_price_history()
        self.pricing_engine = PricingEngine(self.PRODUCT_UNIVERSE)
        self.pricing_engine.start()
        return True

    def enable_trading(self, enable_trading):
        self.trading_enabled = enable_trading
        return True

    def get_trade_history(self):
        trade_history = {}
        for trade in self.trades:
            trade_history[trade.get_time()] = trade
        return trade_history

    @staticmethod
    def get_products():
        return [p.__str__() for p in UNIVERSE]

    def get_product(self, product_name):
        return self.PRODUCT_UNIVERSE[get_pair(product_name)]

    def get_current_price(self, product):
        try:
            return self.PRODUCT_UNIVERSE[get_pair(product)].get_price()
        except KeyError:
            return 0, None

    def get_order_book(self, product_name):
        pair = get_pair(product_name)
        if pair is None:
            return None
        return self.order_books.get(str(pair))

    def get_order_book_snapshot(self, product_name, levels=24):
        book = self.get_order_book(product_name)
        if book is None:
            return None
        _, current_price = self.get_current_price(product_name)
        if current_price is None:
            return None
        self.npc_managers[book.symbol].update(current_price)
        snapshot = book.snapshot(levels=levels)
        snapshot["current_price"] = current_price
        return snapshot

    @staticmethod
    def product_exists(product_name):
        return get_pair(product_name) is not None

    def try_trade(self, trader_id, side, qty, product_name, limit_price=None):
        try:
            if not self.trading_enabled:
                return False, 0.0
            if not self.product_exists(product_name=product_name):
                return False, 0.0
            trader = self.traders[trader_id]
            p = self.get_product(product_name)
            current_time, current_price = p.get_price()
            side_enum = get_side(side)
            book = self.get_order_book(product_name)
            if book is None:
                return False, 0.0
            self.npc_managers[book.symbol].update(current_price)

            if limit_price is None:
                execution = book.execute_market(side=side_enum, quantity=qty)
            else:
                # Product rule: one active (resting) limit order per trader.
                # A new limit order replaces the previous one for this trader.
                book.cancel_trader_orders(trader_id=trader_id)
                execution = book.execute_limit(
                    trader_id=trader_id,
                    side=side_enum,
                    quantity=qty,
                    limit_price=float(limit_price),
                )

            if execution["status"] == "FAILED":
                return False, 0.0

            # Limit order accepted but not filled yet: no position/trade update now.
            if execution["filled_quantity"] <= 0:
                if execution["status"] == "ACCEPTED":
                    return True, float(limit_price)
                return False, 0.0

            executed_qty = execution["filled_quantity"]
            executed_price = execution["average_price"]
            trade = Trade(self.traders[trader_id], side_enum, executed_qty, p.get_pair(), executed_price, current_time)
            # Not allowed to trade twice in the same period
            if current_time in [t for t, tr in self.get_trade_history().items()
                                if tr.get_trader().get_trader_id() == trader_id]:
                return False, 0.0
            # Not allowed to buy/sell if you do not have enough cash
            trade_qty = trade.get_quantity() if trade.get_side() is Side.SELL \
                else trade.get_quantity() * trade.get_rate()
            inventory_qty = trader.get_capital(trade.get_pair().domestic if trade.get_side() is Side.SELL
                                               else trade.get_pair().foreign)
            if trade_qty > inventory_qty:
                return False, 0.0
            trader.record_trade(trade)
            self.trades.append(trade)
            return True, executed_price
        except KeyError as e:
            e.with_traceback(sys.exc_info()[2])
            return False, 0.0

    def create_trader(self, user_name, trader_id=None):
        trader = Trader(user_name=user_name, id=trader_id)
        self.traders[trader.get_trader_id()] = trader
        return trader.get_trader_id()

    def delete_trader(self, user_name):
        trader_id = None
        for id, t in self.traders.items():
            if t.get_user_name() == user_name:
                trader_id = id
        
        if trader_id:
            del self.traders[trader_id]
            return trader_id
        return ''

    def reset_traders(self):
        for id, trader in self.traders.items():
            trader.reset()
    
    def reset_trade_history(self):
        self.trades = []

    def query_trader(self, user_name):
        for trader_id, t in self.traders.items():
            if t.get_user_name() == user_name:
                return trader_id
        return ''

    def get_capitals(self):
        try:
            return {t.get_user_name(): self.get_positions(t.get_trader_id()) for t in self.traders.values()}
        except TypeError as e:
            e.with_traceback(sys.exc_info()[2])

    def get_normalized_capitals(self):
        try:
            return {trader.get_user_name(): sum([self.get_normalized_capital(Currency[curr], amt) for curr, amt in
                                                 self.get_positions(trader.get_trader_id()).items()])
                    for trader in self.traders.values()}
        except TypeError as e:
            e.with_traceback(sys.exc_info()[2])

    def get_normalized_capital(self, currency, amount):
        if self.NORMALIZING_CURRENCY is currency:
            return amount
        for pair, product in self.PRODUCT_UNIVERSE.items():
            if pair.domestic is currency and pair.foreign is self.NORMALIZING_CURRENCY:
                return amount * product.get_price()[1]
            elif pair.domestic is self.NORMALIZING_CURRENCY and pair.foreign is currency:
                return amount * 1 / product.get_price()[1]
        return 0

    def get_positions(self, trader_id):
        try:
            return {c.value: self.traders[trader_id].get_capital(c) for c in Currency}
        except (TypeError, KeyError) as e:
            e.with_traceback(sys.exc_info()[2])

    def get_product_price_history(self, product):
        try:
            return self.PRODUCT_UNIVERSE[get_pair(product)].get_price_history()
        except (KeyError, TypeError) as e:
            e.with_traceback(sys.exc_info()[2])
