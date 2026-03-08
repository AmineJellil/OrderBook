from lib.exchange.LiquidityCurve import generate_bimodal_liquidity_curve
from lib.models.exchange.Side import Side


class NPCManager:
    def __init__(self, order_book):
        self.order_book = order_book

    def _build_curve(self, mid_price):
        pct_bounds = 0.1
        min_price = mid_price * (1 - pct_bounds)
        max_price = mid_price * (1 + pct_bounds)
        return generate_bimodal_liquidity_curve(
            mid=mid_price,
            min_price=min_price,
            max_price=max_price,
            num_levels=40,
            total_liquidity=600_000,
            stddevperc=0.02 / max(mid_price, 0.00001),
            trough_depth=0.45,
            liquidity_skew=0.0,
            density_shape=0.0,
            noise_level=0.02,
            min_pdf=0.0002,
            decimal_places=5,
        )

    def _cancel_invalid_orders(self, curve, mid_price):
        npc_orders = self.order_book.get_orders(trader_id="NPC")
        for order in npc_orders:
            target_exists = order.price in curve
            valid_side = (order.side is Side.BUY and order.price < mid_price) or (
                order.side is Side.SELL and order.price > mid_price
            )
            if not target_exists or not valid_side:
                self.order_book.cancel_order(order.order_id)

    def _fill_missing_liquidity(self, curve, mid_price):
        for price, target_qty in curve.items():
            side = Side.BUY if price < mid_price else Side.SELL
            current_qty = self.order_book.quantity_at_price(price=price, side=side, trader_id="NPC")

            if current_qty == target_qty:
                continue

            if current_qty > 0:
                self.order_book.cancel_orders_at_price(price=price, side=side, trader_id="NPC")

            if target_qty > 0:
                self.order_book.add_limit_order(
                    trader_id="NPC",
                    side=side,
                    quantity=target_qty,
                    price=price,
                )

    def update(self, mid_price):
        curve = self._build_curve(mid_price)
        self._cancel_invalid_orders(curve, mid_price)
        self._fill_missing_liquidity(curve, mid_price)
