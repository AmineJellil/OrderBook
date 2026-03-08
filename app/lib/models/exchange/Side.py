from enum import Enum


class Side(Enum):
    BUY = 'Buy'
    SELL = 'Sell'


def get_side(side):
    return Side[side.upper()]
