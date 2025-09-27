from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta, date
from typing import List

from models.account import Account, AccountCurrencyType
from models.transactions import Transaction, TransactionType
from services.market_data_service import price_lookup
from services.plot.chart_service import total_portfolio_pie_chart
from utils.time_utils import get_pt_yesterday, is_weekend
from models.tickers import Ticker


@dataclass
class PortfolioTimeSeries:
    timestamps: List[str]
    cash: List[float]
    invest: List[float]
    valuation: List[float]
    return_pct: List[float]
    capital_gain: List[float]
    interest_income: List[float]
    dividend_income: List[float]
    total_income: List[float]
    end_date: date


class Portfolio:
    def __init__(self, db):
        self.db = db
        self.cash = 0
        self.capital_gain = 0
        self.invest = 0
        self.interest = 0
        self.dividend = 0
        self.tax_fee = 0
        self.snapshot = defaultdict(float)

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
        elif tx.type == TransactionType.BALANCE_SNAPSHOT:
            self.process_balance_snapshot(tx.account_id, tx.amount)

    def deposit(self, amount):
        self.cash += float(amount)

    def withdraw(self, amount):
        self.cash -= float(amount)

    def buy(self, amount, symbol, quantity, price):
        cost = quantity * price
        self.cash -= float(amount)

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
        self.cash += float(revenue)
        h["quantity"] -= quantity

        realized = revenue - cost_basis

        self.capital_gain += realized
        h["realized_gain"] += realized
        self.invest -= cost_basis

    def process_tax_fee(self, amount):
        self.cash -= float(amount)
        self.tax_fee += amount

    def process_interest(self, amount):
        self.cash += float(amount)
        self.interest += amount

    def process_dividend(self, amount, symbol, date):
        self.cash += float(amount)
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

    def process_balance_snapshot(self, account_id, amount):
        self.cash -= float(self.snapshot[account_id])
        self.cash += float(amount)
        self.snapshot[account_id] = float(amount)


def build_portfolio_timeseries(transactions, portfolio) -> PortfolioTimeSeries:
    timestamps = []
    cash = []
    invest = []
    valuation = []
    return_pct = []
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
        return_pct.append(date_return)

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
        return_pct=return_pct,
        capital_gain=capital_gain,
        interest_income=interest_income,
        dividend_income=dividend_income,
        total_income=total_income,
        end_date=end_date,
    )


def generate_portfolio_tabular_data(db, portfolio: Portfolio, end_date):
    portfolio_list = []
    portfolio_totals = {}
    symbols = list(portfolio.holdings.keys())
    ticker_map = {
        t.symbol: t.name
        for t in db.query(Ticker).filter(Ticker.symbol.in_(symbols)).all()
    }

    for symbol, h in portfolio.holdings.items():
        current_price = float(price_lookup(db, symbol, end_date) or h["avg_cost"])
        avg_price = float(h["avg_cost"])
        quantity = float(h["quantity"])
        valuation = current_price * quantity
        invested = avg_price * quantity
        return_amount = valuation - invested
        return_pct = (return_amount / invested * 100) if invested > 0 else 0

        realized_gain = float(h.get("realized_gain", 0))

        dividend_total = float(h["dividend_total"])
        dividend_pct = (dividend_total / invested * 100) if invested > 0 else 0

        total_profit = return_amount + dividend_total + realized_gain
        total_profit_pct = (total_profit / invested * 100) if invested > 0 else 0

        portfolio_list.append(
            {
                "symbol": symbol,
                "name": ticker_map.get(symbol, ""),
                "quantity": h["quantity"],
                "avg_price": h["avg_cost"],
                "current_price": current_price,
                "invested": invested,
                "valuation": valuation,
                "return_amount": return_amount,
                "return_pct": return_pct,
                "realized_gain": realized_gain,
                "dividend_total": dividend_total,
                "dividend_pct": dividend_pct,
                "total_profit": total_profit,
                "total_profit_pct": total_profit_pct,
            }
        )
    portfolio_list.sort(key=lambda s: s["valuation"], reverse=True)

    portfolio_list.append(
        {
            "symbol": "cash",
            "name": "현금",
            "quantity": 1,
            "avg_price": float(portfolio.cash),
            "current_price": float(portfolio.cash),
            "invested": 0,
            "valuation": float(portfolio.cash),
            "return_amount": 0,
            "return_pct": 0,
            "realized_gain": 0,
            "dividend_total": float(portfolio.interest) - float(portfolio.tax_fee),
            "dividend_pct": 0,
            "total_profit": float(portfolio.interest) - float(portfolio.tax_fee),
            "total_profit_pct": 0,
        }
    )

    portfolio_totals = {
        "invested": sum(s["invested"] for s in portfolio_list),
        "valuation": sum(s["valuation"] for s in portfolio_list),
        "return_amount": sum(s["return_amount"] for s in portfolio_list),
        "dividend_total": sum(s["dividend_total"] for s in portfolio_list),
        "realized_gain": sum(s["realized_gain"] for s in portfolio_list),
    }
    portfolio_totals["total_profit"] = (
        portfolio_totals["return_amount"]
        + portfolio_totals["realized_gain"]
        + portfolio_totals["dividend_total"]
    )
    portfolio_totals["return_pct"] = (
        portfolio_totals["return_amount"] / portfolio_totals["invested"] * 100
        if portfolio_totals["invested"] > 0
        else 0
    )
    portfolio_totals["dividend_pct"] = (
        portfolio_totals["dividend_total"] / portfolio_totals["invested"] * 100
        if portfolio_totals["invested"] > 0
        else 0
    )
    portfolio_totals["total_profit_pct"] = (
        portfolio_totals["total_profit"] / portfolio_totals["invested"] * 100
        if portfolio_totals["invested"] > 0
        else 0
    )
    for stock in portfolio_list:
        stock["valuation_pct"] = (
            stock["valuation"] / portfolio_totals["valuation"] * 100
            if portfolio_totals["valuation"] > 0
            else 0
        )

    return portfolio_list, portfolio_totals


def generate_portfolio_and_timeseries_data(db, currency_type):
    accounts = db.query(Account).order_by(Account.order).all()
    account_ids = [
        account.id
        for account in accounts
        if account.account_currency_type == currency_type
    ]

    portfolio = Portfolio(db)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id.in_(account_ids))
        .order_by(Transaction.date.asc(), Transaction.id.asc())
        .all()
    )
    timeseries = build_portfolio_timeseries(transactions, portfolio)
    return portfolio, timeseries
