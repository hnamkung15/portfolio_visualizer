from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import false, func, or_, true
from sqlalchemy.orm import Session
from db import get_db
from routers.auth import get_current_user
from models.user import User
import requests
from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates

from models.account import Account, AccountCurrencyType, AccountType, AssetBreakdown
from models.transactions import Transaction, TransactionType
from services.account_service import (
    get_checking_account_networth,
    get_stock_account_networth,
)
from services.plot.chart_service import total_portfolio_pie_chart
from services.plot.plot_service import (
    realized_gain_graph,
    return_graph,
    return_pct_graph,
    total_capital_and_cash_graph,
    total_valuation_and_invest_graph,
)
from services.portfolio_service import (
    Portfolio,
    build_portfolio_timeseries,
    generate_portfolio_and_timeseries_data,
    generate_portfolio_tabular_data,
)
from utils.time_utils import get_pt_now

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def get_exchange_rate():
    url = "https://api.manana.kr/exchange/rate.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    usd_krw = None
    as_of = None
    for row in data:
        name = row.get("name", "")
        if "USD" in name and "KRW" in name:
            usd_krw = float(row.get("rate"))
            as_of = row.get("date")
            break
    if usd_krw is None:
        raise RuntimeError("USD/KRW rate not found")

    return usd_krw, get_pt_now().strftime("%Y-%m-%d %H:%M:%S (PT)")


def no_transactions(db, user_id):
    """Check if user has any transactions."""
    # Check if user has any accounts
    user_accounts = db.query(Account).filter(Account.user_id == user_id).all()
    if not user_accounts:
        return True

    # Check if any of the user's accounts have transactions
    account_ids = [account.id for account in user_accounts]
    transaction_count = (
        db.query(Transaction).filter(Transaction.account_id.in_(account_ids)).count()
    )
    return transaction_count == 0


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fx_rate, fx_as_of = get_exchange_rate()
    if no_transactions(db, current_user.id):
        return templates.TemplateResponse(
            "dashboard/dashboard.html",
            {
                "request": request,
                "active": "dashboard",
                "fx_rate": fx_rate,
                "fx_as_of": fx_as_of,
                "total_usd": 0,
                "total_krw": 0,
                "usd_assets": {},
                "krw_assets": {},
                "usd_graphs_html": [],
                "usd_portfolio_list": [],
                "usd_portfolio_totals": {},
                "krw_graphs_html": [],
                "krw_portfolio_list": [],
                "krw_portfolio_totals": {},
                "total_graphs_html": [],
                "no_transaction": 1,
            },
        )

    usd_graphs_html, usd_portfolio_list, usd_portfolio_totals = (
        generate_individual_portfolio_data(db, AccountCurrencyType.USD, current_user.id)
    )
    krw_graphs_html, krw_portfolio_list, krw_portfolio_totals = (
        generate_individual_portfolio_data(db, AccountCurrencyType.KRW, current_user.id)
    )
    total_graphs_html = generate_common_portfolio(db, fx_rate, current_user.id)

    usd_val = usd_portfolio_totals.get("valuation", 0)
    krw_val = krw_portfolio_totals.get("valuation", 0)

    total_usd = usd_val + krw_val / fx_rate
    total_krw = krw_val + usd_val * fx_rate

    usd_assets = {
        "amount_usd": usd_val,
        "amount_krw": usd_val * fx_rate,
        "percent": (usd_val / total_usd) * 100,
    }

    krw_assets = {
        "amount_usd": krw_val / fx_rate,
        "amount_krw": krw_val,
        "percent": (krw_val / total_krw) * 100,
    }

    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "active": "dashboard",
            "fx_rate": fx_rate,
            "fx_as_of": fx_as_of,
            "total_usd": total_usd,
            "total_krw": total_krw,
            "usd_assets": usd_assets,
            "krw_assets": krw_assets,
            "usd_graphs_html": usd_graphs_html,
            "usd_portfolio_list": usd_portfolio_list,
            "usd_portfolio_totals": usd_portfolio_totals,
            "krw_graphs_html": krw_graphs_html,
            "krw_portfolio_list": krw_portfolio_list,
            "krw_portfolio_totals": krw_portfolio_totals,
            "total_graphs_html": total_graphs_html,
            "no_transaction": 0,
        },
    )


def generate_common_portfolio(db, fx_rate, user_id):
    usd_portfolio, usd_timeseries = generate_portfolio_and_timeseries_data(
        db, AccountCurrencyType.USD, user_id
    )
    krw_portfolio, krw_timeseries = generate_portfolio_and_timeseries_data(
        db, AccountCurrencyType.KRW, user_id
    )

    return [
        total_portfolio_pie_chart(db, usd_portfolio, krw_portfolio, fx_rate).to_html(
            full_html=False
        )
    ]


def generate_individual_portfolio_data(db, currency_type, user_id):
    portfolio, timeseries = generate_portfolio_and_timeseries_data(
        db, currency_type, user_id
    )
    if timeseries is None:
        return [], [], {}
    graph_funcs = [
        total_valuation_and_invest_graph,
        return_graph,
        return_pct_graph,
        realized_gain_graph,
        total_capital_and_cash_graph,
    ]
    graphs_html = [
        func(currency_type, timeseries).to_html(full_html=False) for func in graph_funcs
    ]
    portfolio_list, portfolio_totals = generate_portfolio_tabular_data(
        db, portfolio, timeseries.end_date
    )

    return graphs_html, portfolio_list, portfolio_totals


# @router.get("/dashboard")
# def generate_dashboard_data(db: Session = Depends(get_db)):
#     print("come??")
#     usd_graphs_html = generate_portfolio(db, AccountCurrencyType.USD)
#     krw_graphs_html = generate_portfolio(db, AccountCurrencyType.KRW)
#     return {
#         "usd_graphs_html": usd_graphs_html,
#         "krw_graphs_html": krw_graphs_html,
#     }
# # 1) 환율 불러오기
# url = "https://api.manana.kr/exchange/rate.json"
# resp = requests.get(url, timeout=5)
# resp.raise_for_status()
# data = resp.json()

# usd_krw = None
# as_of = None
# for row in data:
#     name = row.get("name", "")
#     if "USD" in name and "KRW" in name:
#         usd_krw = float(row.get("rate"))
#         as_of = row.get("date")
#         break
# if usd_krw is None:
#     raise RuntimeError("USD/KRW rate not found")

# # 2) 총액/리스트 초기화
# usd_assets_value = 0
# krw_assets_value = 0

# usd_accounts_data = []
# usd_networths = []

# krw_accounts_data = []
# krw_networths = []

# usd_asset_breakdown = AssetBreakdown()
# krw_asset_breakdown = AssetBreakdown()

# accounts = db.query(Account).order_by(Account.order).all()

# # 3) 계좌별 처리
# for account in accounts:
#     print()
#     print()
#     print(account.account_name)

#     usd_net = 0
#     krw_net = 0
#     if account.id in [34, 35]:
#         if account.id == 34:  # 새롬 토스 새롬 투자 계좌 (USD)
#             opponent_krw_account_id = 18  # 새롬 토스 새롬 투자 계좌 (KRW)
#         elif account.id == 35:  # 새롬 미래에셋 새롬 투자 계좌 (USD)
#             opponent_krw_account_id = 21  # 새롬 미래에셋 새롬 투자 계좌 (KRW)

#         usd_sum_in = (
#             db.query(func.sum(Transaction.amount))
#             .filter(
#                 Transaction.account_id == account.id,
#                 or_(
#                     Transaction.type == TransactionType.DEPOSIT,
#                     Transaction.type == TransactionType.FX_DEPOSIT,
#                 ),
#             )
#             .scalar()
#             or 0
#         )

#         usd_sum_out = (
#             db.query(func.sum(Transaction.amount))
#             .filter(
#                 Transaction.account_id == account.id,
#                 or_(
#                     Transaction.type == TransactionType.WITHDRAWAL,
#                     Transaction.type == TransactionType.FX_WITHDRAWAL,
#                 ),
#             )
#             .scalar()
#             or 0
#         )
#         usd_net = usd_sum_in - usd_sum_out

#         krw_sum_out = (
#             db.query(func.sum(Transaction.amount))
#             .filter(
#                 Transaction.account_id == opponent_krw_account_id,
#                 Transaction.type == TransactionType.FX_WITHDRAWAL,
#             )
#             .scalar()
#             or 0
#         )

#         krw_sum_in = (
#             db.query(func.sum(Transaction.amount))
#             .filter(
#                 Transaction.account_id == opponent_krw_account_id,
#                 Transaction.type == TransactionType.FX_DEPOSIT,
#             )
#             .scalar()
#             or 0
#         )

#         krw_net = krw_sum_out - krw_sum_in
#         print("usd_net, krw_net")
#         print(usd_net, krw_net)

#     account_networth = 0
#     ab = AssetBreakdown()

#     if account.account_type == AccountType.Checking:
#         account_networth = get_checking_account_networth(db, account)
#         ab += AssetBreakdown(cash=account_networth)
#     elif account.account_type == AccountType.Saving:
#         account_networth = get_checking_account_networth(db, account)
#         ab += AssetBreakdown(saving=account_networth)
#     elif account.account_type == AccountType.STOCK:
#         account_networth, ab = get_stock_account_networth(db, account)
#     else:
#         continue

#     # 프론트에서 바로 쓸 수 있도록 dict로 변환
#     account_info = {
#         "bank_name": account.bank_name,
#         "account_name": account.account_name,
#         "account_type": account.account_type.value,
#         "usd_net": usd_net,
#         "krw_net": krw_net,
#         "breakdown": {
#             "cash": float(ab.cash),
#             "saving": float(ab.saving),
#             "bond": float(ab.bond),
#             "stock": float(ab.stock),
#             "invested": float(ab.invested),
#             "profit": float(ab.profit),
#         },
#     }

#     if account.account_currency_type == AccountCurrencyType.USD:
#         usd_assets_value += account_networth
#         usd_accounts_data.append(account_info)
#         usd_networths.append(float(account_networth))
#         usd_asset_breakdown += ab
#     elif account.account_currency_type == AccountCurrencyType.KRW:
#         krw_assets_value += account_networth
#         krw_accounts_data.append(account_info)
#         krw_networths.append(float(account_networth))
#         krw_asset_breakdown += ab
#     print(account.account_name, ab.invested, ab.profit)

# # 4) USD/KRW 변환 계산
# total_usd = usd_assets_value + krw_assets_value / usd_krw
# total_krw = usd_assets_value * usd_krw + krw_assets_value

# usd_percent = (usd_assets_value / total_usd) * 100 if total_usd else 0
# krw_percent = (krw_assets_value / total_krw) * 100 if total_krw else 0

# total_asset_breakdown_in_usd = usd_asset_breakdown + (krw_asset_breakdown / usd_krw)

# # 5) 응답
# return {
#     "rate": usd_krw,
#     "as_of": as_of or datetime.now().strftime("%Y-%m-%d %H:%M"),
#     "total": {"amount_usd": total_usd, "amount_krw": total_krw},
#     "breakdown": {
#         "usd_assets": {
#             "amount_usd": usd_assets_value,
#             "amount_krw": usd_assets_value * usd_krw,
#             "percent": usd_percent,
#         },
#         "krw_assets": {
#             "amount_usd": krw_assets_value / usd_krw,
#             "amount_krw": krw_assets_value,
#             "percent": krw_percent,
#         },
#     },
#     "usd_accounts": usd_accounts_data,
#     "usd_networths": usd_networths,
#     "krw_accounts": krw_accounts_data,
#     "krw_networths": krw_networths,
#     "type_breakdown": total_asset_breakdown_in_usd.to_list(),
# }
