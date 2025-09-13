from collections import defaultdict

from services.market_data_service import price_lookup


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
