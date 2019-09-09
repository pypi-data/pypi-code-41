from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from terminaltables import AsciiTable

from report.symbolhistory.symbolhistory import gen_loaded_symbol_history
from report.symbolhistory.symbolhistory import SymbolHistory
from robinhood.lib.account.account import account
from robinhood.lib.account.optionevent.optionevent import OptionEvent
from robinhood.lib.account.optionorder.optionorder import OptionOrder
from robinhood.lib.account.stockorder.stockorder import StockOrder
from robinhood.lib.helpers import format_price
from robinhood.lib.helpers import format_quantity
from robinhood.lib.marketplace.equity import Equity
from robinhood.lib.marketplace.marketplace import marketplace


class AccountSummary(object):

    def __init__(self) -> None:
        pass

    def show(self) -> None:
        print(self._gen_reports())

    def _gen_reports(self) -> str:
        symbol_histories = self._get_symbol_histories(
            symbols=account.active_symbols,
            stock_orders=account.stock_orders,
            option_orders=account.option_orders,
            option_events=account.option_events,
        )

        equities = marketplace.get_equities(symbols=account.active_symbols)

        account_summary_report = self._gen_account_summary_report(
            active_symbols=account.active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
            margin_used=account.margin_used,
        )
        individual_report = self._gen_individual_report(
            active_symbols=account.active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )

        return f'{account_summary_report}\n\n{individual_report}'

    def _gen_account_summary_report(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
        margin_used: float,
    ) -> str:
        data = self._gen_account_summary_report_data(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
            margin_used=margin_used,
        )
        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'right',
            1: 'right',
            2: 'right',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
            8: 'right',
        }

        return str(t.table)

    def _gen_individual_report(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
    ) -> str:
        data = self._gen_individual_report_data(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )
        t = AsciiTable(data)
        t.inner_column_border = True
        t.inner_footing_row_border = False
        t.inner_heading_row_border = True
        t.inner_row_border = False
        t.outer_border = False
        t.justify_columns = {
            0: 'right',
            1: 'right',
            2: 'right',
            3: 'right',
            4: 'right',
            5: 'right',
            6: 'right',
            7: 'right',
        }

        return str(t.table)

    def _gen_account_summary_report_data(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
        margin_used: float,
    ) -> List[List[str]]:
        stock_value = self._get_stock_value(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )

        profit_on_stocks = self._get_profit_on_stocks(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )

        option_value = self._get_option_value(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
        )

        account_value = stock_value + option_value - margin_used

        profit_on_options = self._get_profit_on_options(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
        )

        profit_on_call_writes = self._get_profit_on_call_writes(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )

        profit_on_put_writes = self._get_profit_on_put_writes(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
        )

        data = [[
            'Stock Value',
            'Option Value',
            'Margin Used',
            'Account Value',
            '# of Symbols',
            'Profit on Stocks',
            'Profit on Options',
            'Profit on Call Writes',
            'Profit on Put Writes',
        ]]
        data.append([
            format_price(stock_value),
            format_price(option_value),
            format_price(margin_used),
            format_price(account_value),
            format_quantity(len(active_symbols)),
            format_price(profit_on_stocks),
            format_price(profit_on_options),
            format_price(profit_on_call_writes),
            format_price(profit_on_put_writes),
        ])
        return data

    def _gen_individual_report_data(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
    ) -> List[List[str]]:
        data = [[
            'Symbol',
            '# of Shares',
            'Stock Value',
            'Option Value',
            'Settled Profit',
            'Profit on Stocks',
            'Profit on Options',
            'Profit on Call Writes',
            'Profit on Put Writes',
        ]]

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._gen_individual_report_data_for_one_symbol,
                    symbol,
                    active_symbols,
                    symbol_histories,
                    equities,
                )
                for symbol in active_symbols
            ]

        rows: List[List[str]] = []
        for future in as_completed(futures):
            rows.append(future.result())

        data.extend(sorted(rows, key=lambda row: row[0]))

        return data

    def _gen_individual_report_data_for_one_symbol(
        self,
        symbol: str,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
    ) -> List[str]:
        symbol_history = symbol_histories[symbol]
        equity = equities[symbol]
        num_of_shares = symbol_history.sorted_events[-1].context.stock_holding.quantity
        stock_cost_basis = symbol_history.sorted_events[-1].context.stock_holding.stock_cost_basis
        stock_value = num_of_shares * equity.last_price
        stock_profit = stock_value - stock_cost_basis
        settled_profit = symbol_history.sorted_events[-1].context.profit
        option_value = self._get_option_value(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            selected_symbol=symbol,
        )
        option_profit = self._get_profit_on_options(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            selected_symbol=symbol,
        )
        profit_on_call_writes = self._get_profit_on_call_writes(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
            selected_symbol=symbol,
        )
        profit_on_put_writes = self._get_profit_on_put_writes(
            active_symbols=active_symbols,
            symbol_histories=symbol_histories,
            equities=equities,
            selected_symbol=symbol,
        )
        data = [
            symbol,
            format_quantity(num_of_shares),
            format_price(stock_value, empty_for_zero=True),
            format_price(option_value, empty_for_zero=True),
            format_price(settled_profit, empty_for_zero=True),
            format_price(stock_profit, empty_for_zero=True),
            format_price(option_profit, empty_for_zero=True),
            format_price(profit_on_call_writes, empty_for_zero=True),
            format_price(profit_on_put_writes, empty_for_zero=True),
        ]

        return data

    def _get_symbol_histories(
        self,
        symbols: Set[str],
        stock_orders: List[StockOrder],
        option_orders: List[OptionOrder],
        option_events: List[OptionEvent],
    ) -> Dict[str, SymbolHistory]:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    gen_loaded_symbol_history,
                    symbol=symbol,
                    stock_orders=stock_orders,
                    option_orders=option_orders,
                    option_events=option_events,
                )
                for symbol in symbols
            ]

        symbol_histories: Dict[str, SymbolHistory] = {}
        for future in as_completed(futures):
            symbol_history = future.result()
            symbol_histories[symbol_history.symbol] = symbol_history

        return symbol_histories

    def _get_stock_value(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
    ) -> float:
        value = 0.0
        for symbol in active_symbols:
            stock_holding = symbol_histories[symbol].sorted_events[-1].context.stock_holding
            if stock_holding.quantity > 0:
                value += equities[symbol].last_price * stock_holding.quantity

        return value

    def _get_profit_on_stocks(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            stock_holding = symbol_histories[symbol].sorted_events[-1].context.stock_holding
            if stock_holding.quantity > 0:
                profit += (equities[symbol].last_price - stock_holding.avg_unit_price) * stock_holding.quantity

        return profit

    def _get_option_value(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        selected_symbol: Optional[str] = None,
    ) -> float:
        value = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = symbol_histories[symbol].sorted_events[-1].context
            for _, holding in context.option_buy_holding.items():
                value += holding.option_buy_value

        return value

    def _get_profit_on_options(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = symbol_histories[symbol].sorted_events[-1].context
            for _, holding in context.option_buy_holding.items():
                profit += holding.option_buy_profit

        return profit

    def _get_profit_on_call_writes(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = symbol_histories[symbol].sorted_events[-1].context
            for _, holding in context._option_sell_holding.items():
                option_instrument = holding.option_instrument
                stock_price = equities[option_instrument.chain_symbol].last_price
                if option_instrument.instrument_type == 'call':
                    if option_instrument.strike_price >= stock_price:
                        current_profit = holding.avg_unit_price * holding.quantity * 100
                    else:
                        current_profit = (
                            holding.avg_unit_price
                            - stock_price
                            + option_instrument.strike_price
                        ) * holding.quantity * 100

                    profit += current_profit

        return profit

    def _get_profit_on_put_writes(
        self,
        active_symbols: Set[str],
        symbol_histories: Dict[str, SymbolHistory],
        equities: Dict[str, Equity],
        selected_symbol: Optional[str] = None,
    ) -> float:
        profit = 0.0
        for symbol in active_symbols:
            if selected_symbol is not None and symbol != selected_symbol:
                continue

            context = symbol_histories[symbol].sorted_events[-1].context
            for _, holding in context._option_sell_holding.items():
                option_instrument = holding.option_instrument
                stock_price = equities[option_instrument.chain_symbol].last_price
                if option_instrument.instrument_type == 'put':
                    if option_instrument.strike_price <= stock_price:
                        current_profit = holding.avg_unit_price * holding.quantity * 100
                    else:
                        current_profit = (
                            holding.avg_unit_price
                            - option_instrument.strike_price
                            + stock_price
                        ) * holding.quantity * 100

                    profit += current_profit

        return profit
