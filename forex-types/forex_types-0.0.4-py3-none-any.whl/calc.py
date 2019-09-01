"""Calculation methods under Calc class."""

from decimal import Decimal

from forex_types.cash import Cash
from forex_types.currency import Currency
from forex_types.lot_size import LotSize
from forex_types.price import Price, NinjaPrice
from forex_types.direction import Direction


class CalcError(Exception):
    pass


class Calc:

    @staticmethod
    def price_delta(price_1: Price, price_2: Price) -> Decimal:
        """Price subtraction which makes sure subtypes match.

        The idea is to make sure we are not mixing Price and
        NinjaPrice--which makes no sense since the scale is
        radically different (a single yen is worth about a penny)

        Args:
            price_1: price on left side of subtraction
            price_2: price on right side of subtraction
        Return:
            amount in unspecified units of currency
            (NOT a Price--would be out of reasonable range).
            (NOT Cash--we don't know the currency).
        """
        if isinstance(price_1, NinjaPrice) and isinstance(price_2, NinjaPrice):
            return price_1.value - price_2.value
        elif isinstance(price_1, Price) and isinstance(price_2, Price):
            return price_1.value - price_2.value
        else:
            raise CalcError(f"Unexpected price_delta arguments ({price_1}, {price_2})")

    @staticmethod
    def validate_stop(direction: Direction, entry: Price, stop: Price):
        """Raise CalcError if stop is on wrong side of entry or closer than 5 pips."""
        if direction == Direction.LONG:
            pips = entry.pips - stop.pips
            if pips < 5:
                raise CalcError(f"Stop {stop} must be at least 5 pips below {entry} for BUY")
        elif direction == Direction.SHORT:
            pips = stop.pips - entry.pips
            if pips < 5:
                raise CalcError(f"Stop of {stop} must be at least 5 pips above entry {entry} for SELL")

    @classmethod
    def get_lot_size(cls, risk: Cash, direction: Direction, entry: Price, stop: Price) -> LotSize:
        """Calculate lot size that matches risk level.

        Caveat: The value is only approximate because the actual price
        filled at and stopped out at will vary and thus the exact amount
        lost if stopped out will not be exactly the risk amount. Knowing
        this, and because rounded off lot sizes are easier to deal with,
        we round them off to only 2 significant digits.  For example if we
        calculate 2393118 we will return pretty rounded off 2400000.

        Args:
            risk: cash trader is willing to lose if stopped out.
            direction: whether trade is long or short.
            entry: entry price.
            stop: stop loss price.
        Returns:
            LotSize rounded to two significant digits.
        Raises:
            CalcError: if stop is on wrong side of entry per direction.
        """
        # -------------------------------------------------
        # Supporting algebra notes:
        #     LotSize * PriceDelta = Cash
        # Dividing both sides by PriceDelta:
        #     LotSize = Cash/PriceDelta
        # -------------------------------------------------
        # First we need to figure out the price delta.
        cls.validate_stop(direction, entry, stop)
        price_delta = abs(cls.price_delta(entry, stop))
        # Now we use our algebraic answer above. We don't need to
        # worry about dividing by zero because validate_stop passed.
        return LotSize(risk.value / price_delta).get_rounded()

    @classmethod
    def get_cost(cls, size: LotSize, quote: Currency, price: Price):
        """Get cost of a lot of given quote currency at give price."""
        return Cash(size * price.value, quote)

    @classmethod
    def get_trade_cash(
        cls,
        size: LotSize,
        quote: Currency,
        direction: Direction,
        entry_price: Price,
        exit_price: Price
    ) -> Cash:
        """Calculate cash value of trade in quote currency.

        Caveats:
             Interest not figured in.
             Commissions/Spread not figured in.
        Args:
            size: lot size, number of base currency units traded.
            quote: the quote currency
            direction: whether trade is long or short
            entry_price: pair price when position was filled
            exit_price: pair price when position was closed
        Returns:
            Cash in units of quote currency.
        """
        entry_cost = cls.get_cost(size, quote, entry_price)
        exit_cost = cls.get_cost(size, quote, exit_price)
        if direction == Direction.LONG:
            return Cash(exit_cost.value - entry_cost.value, quote)
        else:
            return Cash(entry_cost.value - exit_cost.value, quote)








