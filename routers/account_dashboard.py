from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db
from routers.auth import get_current_user
from models.user import User
from models.transactions import Transaction
from models.account import Account, AccountType

from services.market_data_service import price_lookup
from services.plot.plot_service import (
    cash_and_interest_graph,
    realized_gain_graph,
    return_graph,
    return_pct_graph,
    total_capital_and_cash_graph,
    total_valuation_and_invest_graph,
)
from services.portfolio_service import (
    Portfolio,
    build_portfolio_timeseries,
    generate_portfolio_tabular_data,
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/account_dashboard", response_class=HTMLResponse)
def view_transactions(
    request: Request,
    current_user: User = Depends(get_current_user),
    account_id: int = None,
    db: Session = Depends(get_db),
):
    accounts = (
        db.query(Account)
        .filter(Account.user_id == current_user.id)
        .order_by(Account.order)
        .all()
    )
    if account_id is None:
        return templates.TemplateResponse(
            "account_dashboard/account_dashboard.html",
            {
                "request": request,
                "accounts": accounts,
                "active": "account_dashboard",
                "transactions": [],
                "selected_account": None,
                "graphs_html": [],
                "portfolio_list": [],
                "portfolio_totals": {},
            },
        )

    transactions = []
    selected_account = None

    selected_account = (
        db.query(Account)
        .filter(Account.user_id == current_user.id, Account.id == account_id)
        .first()
    )
    transactions = (
        db.query(Transaction)
        .filter(Transaction.account_id == account_id)
        .order_by(Transaction.date.asc(), Transaction.id.asc())
        .all()
    )

    # Handle empty transactions case
    if len(transactions) == 0:
        return templates.TemplateResponse(
            "account_dashboard/account_dashboard.html",
            {
                "request": request,
                "accounts": accounts,
                "active": "account_dashboard",
                "transactions": [],
                "selected_account": selected_account,
                "graphs_html": [],
                "portfolio_list": [],
                "portfolio_totals": {},
                "has_transactions": False,
            },
        )

    if selected_account.account_type == AccountType.STOCK:
        graph_funcs = [
            total_valuation_and_invest_graph,
            return_graph,
            return_pct_graph,
            realized_gain_graph,
            total_capital_and_cash_graph,
        ]
    else:
        graph_funcs = [
            cash_and_interest_graph,
        ]

    portfolio = Portfolio(db)
    result = build_portfolio_timeseries(transactions, portfolio)

    graphs_html = [
        func(selected_account.account_currency_type, result).to_html(full_html=False)
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
            "graphs_html": graphs_html,
            "portfolio_list": portfolio_list,
            "portfolio_totals": portfolio_totals,
            "cash": portfolio.cash,
            "interest": portfolio.interest,
            "has_transactions": True,
        },
    )
