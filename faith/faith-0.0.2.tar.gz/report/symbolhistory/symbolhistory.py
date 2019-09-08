from concurrent.futures import as_completed
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from terminaltables import AsciiTable

from data.watchlist import ALL
from report.symbolhistory.symbolhistorycontext import SymbolHistoryContext
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_option_event
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_option_order
from report.symbolhistory.symbolhistoryevent import symbol_history_event_from_stock_order
from report.symbolhistory.symbolhistoryevent import SymbolHistoryEvent
from robinhood.lib.account.account import Account
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.stockorder.stockorder import StockOrder
from robinhood.lib.helpers import format_optional_price
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import format_quantity


class SymbolHistory(object):

    def __init__(
        self,
        symbol: str,
        stock_orders: Optional[List[StockOrder]] = None,
        option_orders: Optional[List[OptionOrder]] = None,
        option_events: Optional[List[OptionEvent]] = None,
    ) -> None:
        self._symbol = symbol
        self._instrument_id = ALL[symbol]
        self._stock_orders = stock_orders
        self._option_orders = option_orders
        self._option_events = option_events
        self._events: List[SymbolHistoryEvent] = []
        self._context = SymbolHistoryContext(symbol=symbol)
        self._history_generated = False

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sorted_events(self) -> List[SymbolHistoryEvent]:
        if not self._history_generated:
            self.gen_history()

        return sorted(self._events, key=lambda e: e.event_ts)

    def show(self) -> None:
        t = AsciiTable(self._gen_ascii_tbl_data())
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'center',
            1: 'center',
            2: 'center',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
        }
        print(t.table)

    def _gen_ascii_tbl_data(self) -> List[List[str]]:
        if not self._history_generated:
            self.gen_history()

        data = [[
            'Date',
            'Event',
            'Symbol',
            'Quantity',
            'Price',
            '# of Shares',
            'Avg Price',
            'Cumulative Profit',
        ]]

        for event in sorted(self._events, key=lambda e: e.event_ts):
            # could be option legs from vertical
            if event.context is None:
                continue

            data.append(
                [
                    event.formatted_ts,
                    event.event_name,
                    event.symbol,
                    format_quantity(event.quantity),
                    format_optional_price(event.unit_price),
                    format_quantity(event.context.stock_holding.quantity),
                    format_price(event.context.stock_holding.avg_unit_price),
                    format_price(event.context.profit),
                ],
            )

        return data

    def _gen_raw_events(self) -> List[SymbolHistoryEvent]:
        if self._stock_orders is None:
            self._stock_orders, self._option_orders, self._option_events = self._get_raw_data()

        events: List[SymbolHistoryEvent] = []

        assert self._stock_orders is not None
        events.extend(self._convert_stock_orders_to_symbol_history_events(stock_orders=self._stock_orders))

        assert self._option_orders is not None
        events.extend(self._convert_option_orders_to_symbol_history_events(option_orders=self._option_orders))

        assert self._option_events is not None
        events.extend(self._convert_option_events_to_symbol_history_events(option_events=self._option_events))

        return events

    def _convert_stock_orders_to_symbol_history_events(
        self,
        stock_orders: List[StockOrder],
    ) -> Iterator[SymbolHistoryEvent]:
        for stock_order in stock_orders:
            if stock_order.instrument_id != self._instrument_id:
                continue

            symbol_history_event = symbol_history_event_from_stock_order(
                symbol=self._symbol,
                stock_order=stock_order,
            )
            if symbol_history_event is not None:
                yield symbol_history_event

    def _convert_option_orders_to_symbol_history_events(
        self,
        option_orders: List[OptionOrder],
    ) -> Iterator[SymbolHistoryEvent]:
        for option_order in option_orders:
            if option_order.chain_symbol != self._symbol:
                continue

            symbol_history_event = symbol_history_event_from_option_order(
                symbol=self._symbol,
                option_order=option_order,
            )
            if symbol_history_event is not None:
                yield symbol_history_event

    def _convert_option_events_to_symbol_history_events(
        self,
        option_events: List[OptionEvent],
    ) -> Iterator[SymbolHistoryEvent]:
        for option_event in option_events:
            if option_event.option_instrument.chain_symbol != self._symbol:
                continue

            symbol_history_event = symbol_history_event_from_option_event(option_event=option_event)
            if symbol_history_event is not None:
                yield symbol_history_event

    def gen_history(self) -> None:
        self._events = self._gen_raw_events()
        self._enrich_raw_events()
        self._history_generated = True

    def _enrich_raw_events(self) -> None:
        for event in sorted(self._events, key=lambda e: e.event_ts):
            if event.event_name in ('SHORT PUT', 'SHORT CALL'):
                assert event.unit_price is not None
                assert event.option_order.num_of_legs == 1
                self._context.sell_to_open(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                    option_instrument=event.option_order.legs[0].option_instrument,
                )
            elif event.event_name in ('LONG PUT', 'LONG CALL'):
                assert event.unit_price is not None
                assert event.option_order.num_of_legs == 1
                self._context.buy_to_open(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                    option_instrument=event.option_order.legs[0].option_instrument,
                )
            elif event.event_name in {'ROLLING CALL', 'ROLLING PUT'}:
                assert event.unit_price is not None
                closing_option_instrument = event.option_rolling_order.closing_leg.option_instrument
                unit_price = self._context.option_sell_holding[closing_option_instrument.symbol].avg_unit_price
                self._context.buy_to_close(
                    symbol=closing_option_instrument.symbol,
                    quantity=int(event.quantity),
                    price=unit_price,
                )

                opening_option_instrument = event.option_rolling_order.opening_leg.option_instrument
                self._context.sell_to_open(
                    symbol=opening_option_instrument.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price + unit_price,
                    option_instrument=opening_option_instrument,
                )
            elif event.event_name == 'SHORT CALL SPREAD':
                for leg in event.option_order.legs:
                    if leg.side == 'buy':
                        self._context.buy_to_open(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                            option_instrument=leg.option_instrument,
                        )
                    else:
                        self._context.sell_to_open(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                            option_instrument=leg.option_instrument,
                        )
            elif event.event_name == 'OPTION EXPIRATION':
                self._context.option_expire(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                )
            elif event.event_name == 'BUY TO CLOSE':
                assert event.unit_price is not None
                self._context.buy_to_close(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                )
            elif event.event_name == 'SELL TO CLOSE':
                assert event.unit_price is not None
                self._context.sell_to_close(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                )
            elif event.event_name == 'CALL ASSIGNMENT':
                assert event.unit_price is not None
                self._context.call_assignment(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                )
            elif event.event_name == 'PUT ASSIGNMENT':
                instrument = event.option_event.option_instrument
                assert event.unit_price is not None
                self._context.put_asignment(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=event.unit_price,
                    strike_price=instrument.strike_price,
                )
            elif event.event_name == 'OPTION EXERCISE':
                option_instrument = event.option_event.option_instrument
                option_avg_price = self._context.option_buy_holding[event.symbol].avg_unit_price
                event.unit_price = option_instrument.strike_price + option_avg_price
                self._context.call_exercise(
                    symbol=event.symbol,
                    quantity=int(event.quantity),
                    price=option_avg_price,
                    strike_price=option_instrument.strike_price,
                )
            elif event.event_name in ('LIMIT BUY', 'MARKET BUY'):
                assert event.unit_price is not None
                self._context.limit_or_market_buy_stock(
                    quantity=int(event.quantity),
                    price=event.unit_price,
                )
            elif event.event_name in ('LIMIT SELL', 'MARKET SELL'):
                assert event.unit_price is not None
                self._context.limit_or_market_sell_stock(
                    quantity=int(event.quantity),
                    price=event.unit_price,
                )
            elif event.event_name in {
                'FIG LEAF',
                'LONG CALL SPREAD',
                'LONG PUT SPREAD',
                'SHORT PUT SPREAD',
                'CUSTOM',
                'IRON CONDOR',
            }:
                for leg in event.option_order.legs:
                    if leg.side == 'buy':
                        self._context.buy_to_open(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                            option_instrument=leg.option_instrument,
                        )
                    else:
                        self._context.sell_to_open(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                            option_instrument=leg.option_instrument,
                        )
            elif event.event_name in {
                'FIG LEAF CLOSE',
                'LONG CALL SPREAD CLOSE',
                'LONG CALL CLOSE',
                'LONG PUT CLOSE',
                'LONG PUT SPREAD CLOSE',
                'SHORT PUT SPREAD CLOSE',
                'CUSTOM CLOSE',
                'IRON CONDOR CLOSE',
            }:
                for leg in event.option_order.legs:
                    if leg.side == 'buy':
                        self._context.buy_to_close(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                        )
                    else:
                        self._context.sell_to_close(
                            symbol=leg.option_instrument.symbol,
                            quantity=int(leg.quantity),
                            price=leg.price,
                        )
            else:
                raise NotImplementedError(event.event_name)

            event.add_context(
                symbol_history_context_snapshot=self._context.take_snapshot(),
            )

    def _get_raw_data(self) -> Tuple[List[StockOrder], List[OptionOrder], List[OptionEvent]]:
        account = Account()

        with ThreadPoolExecutor() as executor:
            futures: List[Future[List[Any]]] = [
                executor.submit(account.get_stock_orders),
                executor.submit(account.get_option_orders),
                executor.submit(account.get_option_events),
            ]

        stock_orders: List[StockOrder] = []
        option_orders: List[OptionOrder] = []
        option_events: List[OptionEvent] = []
        for future in as_completed(futures):
            results: List[Any] = future.result()
            if len(results) == 0:
                continue

            if isinstance(results[0], StockOrder):
                stock_orders = results
            elif isinstance(results[0], OptionOrder):
                option_orders = results
            elif isinstance(results[0], OptionEvent):
                option_events = results

        return (stock_orders, option_orders, option_events)


def gen_loaded_symbol_history(
    symbol: str,
    stock_orders: List[StockOrder],
    option_orders: List[OptionOrder],
    option_events: List[OptionEvent],
) -> SymbolHistory:
    symbol_history = SymbolHistory(
        symbol=symbol,
        stock_orders=stock_orders,
        option_orders=option_orders,
        option_events=option_events,
    )
    symbol_history.gen_history()
    return symbol_history
