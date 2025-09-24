from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta, date
from typing import List

from models.transactions import TransactionType
from services.market_data_service import price_lookup
from utils.time_utils import get_pt_yesterday, is_weekend


@dataclass
class PortfolioTimeSeries:
    timestamps: List[str]
    cash: List[float]
    invest: List[float]
    valuation: List[float]
    returns_pct: List[float]
    capital_gain: List[float]
    interest_income: List[float]
    dividend_income: List[float]
    total_income: List[float]
    end_date: date


def build_portfolio_timeseries(transactions, portfolio) -> PortfolioTimeSeries:
    timestamps = []
    cash = []
    invest = []
    valuation = []
    returns_pct = []
    capital_gain = []
    interest_income = []
    dividend_income = []
    total_income = []

    start_date = transactions[0].date
    end_date = get_pt_yesterday()
    num_days = (end_date - start_date).days + 1

    tx_idx = 0
    n = len(transactions)

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)

        while tx_idx < n and transactions[tx_idx].date == current_date:
            tx = transactions[tx_idx]
            portfolio.process_tx(tx, current_date)
            tx_idx += 1

        if is_weekend(current_date):
            continue

        timestamps.append(current_date.strftime("%Y-%m-%d"))

        inv = float(portfolio.invest)
        val = portfolio.process_valuation(current_date)

        if inv == 0:
            date_return = 0
        else:
            date_return = (val - inv) / inv * 100
        cash.append(portfolio.cash)
        invest.append(inv)
        valuation.append(val)
        returns_pct.append(date_return)

        capital_gain.append(portfolio.capital_gain)
        interest_income.append(portfolio.interest)
        dividend_income.append(portfolio.dividend)
        total_income.append(
            portfolio.capital_gain + portfolio.interest + portfolio.dividend
        )
    return PortfolioTimeSeries(
        timestamps=timestamps,
        cash=cash,
        invest=invest,
        valuation=valuation,
        returns_pct=returns_pct,
        capital_gain=capital_gain,
        interest_income=interest_income,
        dividend_income=dividend_income,
        total_income=total_income,
        end_date=end_date,
    )


class Portfolio:
    def __init__(self, db):
        self.db = db
        self.cash = 0
        self.capital_gain = 0
        self.invest = 0
        self.interest = 0
        self.dividend = 0
        self.tax_fee = 0

        self.holdings = defaultdict(
            lambda: {
                "quantity": 0,
                "avg_cost": 0,
                "dividend_total": 0,
                "dividends": [],
                "realized_gain": 0,
            }
        )

    def process_tx(self, tx, current_date):
        if tx.type in [TransactionType.DEPOSIT, TransactionType.FX_DEPOSIT]:
            self.deposit(tx.amount)
        elif tx.type in [
            TransactionType.WITHDRAWAL,
            TransactionType.FX_WITHDRAWAL,
        ]:
            self.withdraw(tx.amount)
        elif tx.type == TransactionType.BUY:
            self.buy(tx.amount, tx.symbol, tx.quantity, tx.price)
        elif tx.type == TransactionType.SELL:
            self.sell(tx.amount, tx.symbol, tx.quantity, tx.price)
        elif tx.type == TransactionType.TAX_FEE:
            self.process_tax_fee(tx.amount)
        elif tx.type == TransactionType.INTEREST:
            self.process_interest(tx.amount)
        elif tx.type == TransactionType.DIVIDEND:
            self.process_dividend(tx.amount, tx.symbol, current_date)
        elif tx.type == TransactionType.VESTING:
            self.process_vesting(tx.amount, tx.symbol, tx.quantity, tx.price)

    def deposit(self, amount):
        self.cash += amount

    def withdraw(self, amount):
        self.cash -= amount

    def buy(self, amount, symbol, quantity, price):
        cost = quantity * price
        self.cash -= amount

        h = self.holdings[symbol]
        total_cost = h["avg_cost"] * h["quantity"] + cost
        h["quantity"] += quantity
        h["avg_cost"] = total_cost / h["quantity"]

        self.invest += cost

    def sell(self, amount, symbol, quantity, price):
        h = self.holdings[symbol]
        if quantity > h["quantity"]:
            raise ValueError("Not enough holdings to sell")

        revenue = quantity * price
        cost_basis = h["avg_cost"] * quantity
        self.cash += revenue
        h["quantity"] -= quantity

        realized = revenue - cost_basis

        self.capital_gain += realized
        h["realized_gain"] += realized
        self.invest -= cost_basis

    def process_tax_fee(self, amount):
        self.cash -= amount
        self.tax_fee += amount

    def process_interest(self, amount):
        self.cash += amount
        self.interest += amount

    def process_dividend(self, amount, symbol, date):
        self.cash += amount
        self.dividend += amount

        h = self.holdings[symbol]
        h["dividend_total"] += amount
        h["dividends"].append((date, amount))

    def process_vesting(self, amount, symbol, quantity, price):
        cost = quantity * price

        h = self.holdings[symbol]
        total_cost = h["avg_cost"] * h["quantity"] + cost
        h["quantity"] += quantity
        h["avg_cost"] = total_cost / h["quantity"]

        self.invest += amount

    def process_valuation(self, date):
        print("process_valuation", date)
        valuation = 0
        for symbol, h in self.holdings.items():
            price = price_lookup(self.db, symbol, date)
            if price:
                # print("[portfolio_service], price found", date, symbol, price)
                valuation += float(h["quantity"]) * price
            else:
                # print("[portfolio_service], price NOT found", date, symbol)
                valuation += float(h["quantity"]) * float(h["avg_cost"])
        return valuation

    def print_holdings(self):
        print("=== Portfolio Holdings ===")
        if not self.holdings:
            print("No holdings")
            return

        for symbol, h in self.holdings.items():
            print(
                f"Symbol: {symbol}, "
                f"Quantity: {h['quantity']}, "
                f"Avg Cost: {h['avg_cost']:.2f}"
            )
        print("==========================")
