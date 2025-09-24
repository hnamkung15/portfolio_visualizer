from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db
from models.tickers import Ticker
from models.transactions import Transaction
from models.account import Account, AccountType

from services.market_data_service import price_lookup
from services.plot_service import (
    realized_gain_graph,
    return_pct_graph,
    total_capital_and_cash_graph,
    total_valuation_and_invest_graph,
)
from services.portfolio_service import Portfolio, build_portfolio_timeseries

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def generate_portfolio_tabular_data(db, portfolio, end_date):
    portfolio_list = []
    portfolio_totals = {}
    symbols = list(portfolio.holdings.keys())
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

    return portfolio_list, portfolio_totals


@router.get("/account_dashboard", response_class=HTMLResponse)
def view_transactions(
    request: Request,
    account_id: int = None,
    db: Session = Depends(get_db),
):
    accounts = db.query(Account).order_by(Account.order).all()
    if account_id is None:
        return templates.TemplateResponse(
            "account_dashboard/account_dashboard.html",
            {
                "request": request,
                "accounts": accounts,
                "active": "account_dashboard",
                "transactions": [],
                "selected_account": None,
                "graph_html_1": "",
                "graph_html_2": "",
                "graph_html_3": "",
                "graph_html_4": "",
                "portfolio_list": [],
                "portfolio_totals": {},
            },
        )

    transactions = []
    selected_account = None

    selected_account = db.query(Account).get(account_id)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.date.asc(), Transaction.id.asc())
        .all()
    )

    if selected_account.account_type == AccountType.STOCK:

        portfolio = Portfolio(db)
        result = build_portfolio_timeseries(transactions, portfolio)

        graph_funcs = [
            total_valuation_and_invest_graph,
            return_pct_graph,
            realized_gain_graph,
            total_capital_and_cash_graph,
        ]

        graphs_html = [
            func(selected_account.account_currency_type, result).to_html(
                full_html=False
            )
            for func in graph_funcs
        ]
        portfolio_list, portfolio_totals = generate_portfolio_tabular_data(
            db, portfolio, result.end_date
        )

    transactions.sort(key=lambda t: (t.date, t.id), reverse=True)

    return templates.TemplateResponse(
        "account_dashboard/account_dashboard.html",
        {
            "request": request,
            "accounts": accounts,
            "active": "account_dashboard",
            "transactions": transactions,
            "selected_account": selected_account,
            "graph_html_1": graphs_html[0],
            "graph_html_2": graphs_html[1],
            "graph_html_3": graphs_html[2],
            "graph_html_4": graphs_html[3],
            "portfolio_list": portfolio_list,
            "portfolio_totals": portfolio_totals,
        },
    )
