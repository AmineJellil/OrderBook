from dataclasses import dataclass
from threading import Lock

from lib.models.exchange.Side import Side


@dataclass
class BookOrder:
    order_id: int
    trader_id: str
    side: Side
    quantity: int
    price: float


class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._bids = []
        self._asks = []
        self._next_order_id = 1
        self._lock = Lock()

    def _new_order_id(self):
        order_id = self._next_order_id
        self._next_order_id += 1
        return order_id

    def _insert_order(self, order: BookOrder):
        if order.side is Side.BUY:
            self._bids.append(order)
            self._bids.sort(key=lambda o: o.price, reverse=True)
        else:
            self._asks.append(order)
            self._asks.sort(key=lambda o: o.price)

    def add_limit_order(self, trader_id: str, side: Side, quantity: int, price: float):
        with self._lock:
            order = BookOrder(
                order_id=self._new_order_id(),
                trader_id=trader_id,
                side=side,
                quantity=int(quantity),
                price=float(price),
            )
            self._insert_order(order)
            return order

    def get_orders(self, trader_id=None, side=None):
        with self._lock:
            orders = self._bids + self._asks
            if trader_id is not None:
                orders = [o for o in orders if o.trader_id == trader_id]
            if side is not None:
                orders = [o for o in orders if o.side is side]
            return list(orders)

    def cancel_order(self, order_id):
        with self._lock:
            for book_side in (self._bids, self._asks):
                for idx, order in enumerate(book_side):
                    if order.order_id == order_id:
                        book_side.pop(idx)
                        return True
            return False

    def cancel_trader_orders(self, trader_id: str):
        with self._lock:
            self._bids = [o for o in self._bids if o.trader_id != trader_id]
            self._asks = [o for o in self._asks if o.trader_id != trader_id]

    def cancel_orders_at_price(self, price: float, side: Side, trader_id=None):
        with self._lock:
            book_side = self._bids if side is Side.BUY else self._asks
            kept_orders = []
            for order in book_side:
                same_owner = trader_id is None or order.trader_id == trader_id
                if order.price == price and same_owner:
                    continue
                kept_orders.append(order)
            if side is Side.BUY:
                self._bids = kept_orders
            else:
                self._asks = kept_orders

    def quantity_at_price(self, price: float, side: Side, trader_id=None):
        with self._lock:
            book_side = self._bids if side is Side.BUY else self._asks
            total = 0
            for order in book_side:
                if order.price != price:
                    continue
                if trader_id is not None and order.trader_id != trader_id:
                    continue
                total += order.quantity
            return total

    def snapshot(self, levels=24):
        with self._lock:
            bids = [(o.order_id, o.price, o.quantity) for o in self._bids[:levels]]
            asks = [(o.order_id, o.price, o.quantity) for o in self._asks[:levels]]
            best_bid = self._bids[0].price if self._bids else None
            best_ask = self._asks[0].price if self._asks else None
            return {"bids": bids, "asks": asks, "best_bid": best_bid, "best_ask": best_ask}

    def execute_market(self, side: Side, quantity: int):
        with self._lock:
            resting = self._asks if side is Side.BUY else self._bids
            remaining = quantity
            total_cost = 0.0
            filled = 0
            fills = []

            while remaining > 0 and resting:
                best = resting[0]
                trade_qty = min(remaining, best.quantity)
                remaining -= trade_qty
                filled += trade_qty
                total_cost += trade_qty * best.price
                fills.append(
                    {
                        "counterparty_trader_id": best.trader_id,
                        "quantity": trade_qty,
                        "price": best.price,
                    }
                )
                best.quantity -= trade_qty
                if best.quantity == 0:
                    resting.pop(0)

            avg_price = (total_cost / filled) if filled > 0 else 0.0
            status = "FILLED" if remaining == 0 and filled > 0 else ("PARTIAL" if filled > 0 else "FAILED")
            return {
                "filled_quantity": filled,
                "remaining_quantity": remaining,
                "average_price": avg_price,
                "status": status,
                "fills": fills,
            }

    def execute_limit(self, trader_id: str, side: Side, quantity: int, limit_price: float):
        with self._lock:
            resting = self._asks if side is Side.BUY else self._bids
            remaining = quantity
            total_cost = 0.0
            filled = 0
            fills = []

            def is_crossing(best_price):
                if side is Side.BUY:
                    return best_price <= limit_price
                return best_price >= limit_price

            while remaining > 0 and resting and is_crossing(resting[0].price):
                best = resting[0]
                trade_qty = min(remaining, best.quantity)
                remaining -= trade_qty
                filled += trade_qty
                total_cost += trade_qty * best.price
                fills.append(
                    {
                        "counterparty_trader_id": best.trader_id,
                        "quantity": trade_qty,
                        "price": best.price,
                    }
                )
                best.quantity -= trade_qty
                if best.quantity == 0:
                    resting.pop(0)

            resting_order_id = None
            if remaining > 0:
                resting_order = BookOrder(
                    order_id=self._new_order_id(),
                    trader_id=trader_id,
                    side=side,
                    quantity=remaining,
                    price=float(limit_price),
                )
                self._insert_order(resting_order)
                resting_order_id = resting_order.order_id

            avg_price = (total_cost / filled) if filled > 0 else 0.0
            if filled == 0 and remaining > 0:
                status = "ACCEPTED"
            elif filled > 0 and remaining > 0:
                status = "PARTIAL"
            elif filled > 0 and remaining == 0:
                status = "FILLED"
            else:
                status = "FAILED"

            return {
                "filled_quantity": filled,
                "remaining_quantity": remaining,
                "average_price": avg_price,
                "status": status,
                "order_id": resting_order_id,
                "limit_price": float(limit_price),
                "fills": fills,
            }

    def resolve_crossed_book(self):
        """Match resting orders while best bid crosses best ask."""
        with self._lock:
            fills = []
            while self._bids and self._asks and self._bids[0].price >= self._asks[0].price:
                best_bid = self._bids[0]
                best_ask = self._asks[0]
                trade_qty = min(best_bid.quantity, best_ask.quantity)
                trade_price = best_ask.price

                fills.append(
                    {
                        "buy_trader_id": best_bid.trader_id,
                        "sell_trader_id": best_ask.trader_id,
                        "quantity": trade_qty,
                        "price": trade_price,
                    }
                )

                best_bid.quantity -= trade_qty
                best_ask.quantity -= trade_qty

                if best_bid.quantity == 0:
                    self._bids.pop(0)
                if best_ask.quantity == 0:
                    self._asks.pop(0)

            return fills
