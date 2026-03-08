from enum import Enum


class Currency(Enum):
    EUR = 'EUR'
    GBP = 'GBP'


class CurrencyPair:
    def __init__(self, domestic, foreign):
        self.domestic = domestic
        self.foreign = foreign

    def __str__(self):
        return self.domestic.value + self.foreign.value


EURGBP = CurrencyPair(Currency.EUR, Currency.GBP)

UNIVERSE = [EURGBP]


def get_pair(name):
    return globals()[name]
