from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db
from models.tickers import Ticker
from models.transactions import Transaction, TransactionType
from models.account import Account, AccountType
from datetime import datetime, timedelta

from services.market_data_service import price_lookup
from services.plot_service import graphs
from services.portfolio_service import Portfolio
from utils.time_utils import get_kst_yesterday, is_weekend

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/account_dashboard", response_class=HTMLResponse)
def view_transactions(
    request: Request,
    account_id: int = None,
    db: Session = Depends(get_db),
):
    accounts = db.query(Account).order_by(Account.order).all()
    transactions = []
    selected_account = None

    graph_html_1 = "<p>No graph available</p>"
    graph_html_2 = "<p>No graph available</p>"
    graph_html_3 = "<p>No graph available</p>"
    graph_html_4 = "<p>No graph available</p>"
    portfolio_list = []
    portfolio_totals = {}

    if account_id:
        selected_account = db.query(Account).get(account_id)
        transactions = (
            db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.date.asc(), Transaction.id.asc())
            .all()
        )

        if selected_account.account_type == AccountType.STOCK:

            portfolio = Portfolio(db)

            timestamps = []

            cash = []
            invest = []
            valuation = []
            returns = []

            capital_gain = []
            interest_income = []
            dividend_income = []
            total_income = []

            start_date = transactions[0].date
            end_date = get_kst_yesterday()
            num_days = (end_date - start_date).days + 1

            tx_idx = 0
            n = len(transactions)

            for i in range(num_days):
                current_date = start_date + timedelta(days=i)

                while tx_idx < n and transactions[tx_idx].date == current_date:
                    tx = transactions[tx_idx]
                    if tx.type in [TransactionType.DEPOSIT, TransactionType.FX_DEPOSIT]:
                        portfolio.deposit(tx.amount)
                    elif tx.type in [
                        TransactionType.WITHDRAWAL,
                        TransactionType.FX_WITHDRAWAL,
                    ]:
                        portfolio.withdraw(tx.amount)
                    elif tx.type == TransactionType.BUY:
                        portfolio.buy(tx.amount, tx.symbol, tx.quantity, tx.price)
                    elif tx.type == TransactionType.SELL:
                        portfolio.sell(tx.amount, tx.symbol, tx.quantity, tx.price)
                    elif tx.type == TransactionType.TAX_FEE:
                        portfolio.process_tax_fee(tx.amount)
                    elif tx.type == TransactionType.INTEREST:
                        portfolio.process_interest(tx.amount)
                    elif tx.type == TransactionType.DIVIDEND:
                        portfolio.process_dividend(tx.amount, tx.symbol, current_date)
                    elif tx.type == TransactionType.VESTING:
                        portfolio.process_vesting(
                            tx.amount, tx.symbol, tx.quantity, tx.price
                        )

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
                returns.append(date_return)

                capital_gain.append(portfolio.capital_gain)
                interest_income.append(portfolio.interest)
                dividend_income.append(portfolio.dividend)
                total_income.append(
                    portfolio.capital_gain + portfolio.interest + portfolio.dividend
                )

            fig_1, fig_2, fig_3, fig_4 = graphs(
                selected_account.account_currency_type,
                timestamps,
                cash,
                invest,
                valuation,
                returns,
                capital_gain,
                interest_income,
                dividend_income,
                total_income,
            )

            graph_html_1 = fig_1.to_html(full_html=False)
            graph_html_2 = fig_2.to_html(full_html=False)
            graph_html_3 = fig_3.to_html(full_html=False)
            graph_html_4 = fig_4.to_html(full_html=False)

            symbols = [s for s, h in portfolio.holdings.items()]
            ticker_map = {
                t.symbol: t.name
                for t in db.query(Ticker).filter(Ticker.symbol.in_(symbols)).all()
            }

            for symbol, h in portfolio.holdings.items():
                current_price = price_lookup(db, symbol, end_date) or h["avg_cost"]
                valuation = float(current_price) * float(h["quantity"])
                invested = float(h["avg_cost"] * h["quantity"])
                returns_amount = valuation - invested
                returns_pct = (returns_amount / invested * 100) if invested > 0 else 0

                realized_gain = float(h.get("realized_gain", 0))

                dividend_total = float(h["dividend_total"])
                dividend_pct = (dividend_total / invested * 100) if invested > 0 else 0

                total_profit = returns_amount + dividend_total + realized_gain
                total_profit_pct = (
                    (total_profit / invested * 100) if invested > 0 else 0
                )

                portfolio_list.append(
                    {
                        "symbol": symbol,
                        "name": ticker_map.get(symbol, ""),
                        "quantity": h["quantity"],
                        "avg_price": h["avg_cost"],
                        "current_price": current_price,
                        "invested": invested,
                        "valuation": valuation,
                        "returns_amount": returns_amount,  # 평가수익
                        "returns_pct": returns_pct,
                        "realized_gain": realized_gain,
                        "dividend_total": dividend_total,  # 총 배당금
                        "dividend_pct": dividend_pct,
                        "total_profit": total_profit,  # 총 수익
                        "total_profit_pct": total_profit_pct,
                    }
                )
            portfolio_totals = {
                "invested": sum(s["invested"] for s in portfolio_list),
                "valuation": sum(s["valuation"] for s in portfolio_list),
                "returns_amount": sum(s["returns_amount"] for s in portfolio_list),
                "dividend_total": sum(s["dividend_total"] for s in portfolio_list),
                "realized_gain": sum(s["realized_gain"] for s in portfolio_list),
            }
            portfolio_totals["total_profit"] = (
                portfolio_totals["returns_amount"]
                + portfolio_totals["realized_gain"]
                + portfolio_totals["dividend_total"]
            )
            portfolio_totals["returns_pct"] = (
                portfolio_totals["returns_amount"] / portfolio_totals["invested"] * 100
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
            portfolio_list.sort(key=lambda s: s["valuation"], reverse=True)
        transactions.sort(key=lambda t: (t.date, t.id), reverse=True)

    return templates.TemplateResponse(
        "account_dashboard/account_dashboard.html",
        {
            "request": request,
            "accounts": accounts,
            "active": "account_dashboard",
            "transactions": transactions,
            "selected_account": selected_account,
            "graph_html_1": graph_html_1,
            "graph_html_2": graph_html_2,
            "graph_html_3": graph_html_3,
            "graph_html_4": graph_html_4,
            "portfolio_list": portfolio_list,
            "portfolio_totals": portfolio_totals,
        },
    )
