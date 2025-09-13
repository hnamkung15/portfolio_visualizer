from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from db import get_db
import requests
from datetime import datetime
from fastapi.templating import Jinja2Templates
from i18n_helpers import get_templates_with_i18n

from models.account import Account, AccountCurrencyType, AccountType, AssetBreakdown
from models.transactions import Transaction, TransactionType
from services.account_service import (
    get_checking_account_networth,
    get_stock_account_networth,
)

templates = Jinja2Templates(directory="templates")
router = APIRouter()



@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    i18n_templates = get_templates_with_i18n(request)
    return i18n_templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "active": "dashboard",
        },
    )


# @router.get("/api/download_data")
# def download_data(db: Session = Depends(get_db)):
#     print("download_data")

#     accounts = db.query(Account).order_by(Account.order).all()
#     for account in accounts:
#         if account.account_type != AccountType.STOCK:
#             continue


@router.get("/api/dashboard")
def generate_dashboard_data(db: Session = Depends(get_db)):
    # 1) 환율 불러오기
    url = "https://api.manana.kr/exchange/rate.json"
    resp = requests.get(url, timeout=5)
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

    # 2) 총액/리스트 초기화
    usd_assets_value = 0
    krw_assets_value = 0

    usd_accounts_data = []
    usd_networths = []

    krw_accounts_data = []
    krw_networths = []

    usd_asset_breakdown = AssetBreakdown()
    krw_asset_breakdown = AssetBreakdown()

    accounts = db.query(Account).order_by(Account.order).all()

    # 3) 계좌별 처리
    for account in accounts:
        print()
        print()
        print(account.account_name)

        usd_net = 0
        krw_net = 0
        if account.id in [34, 35]:
            if account.id == 34:  # 새롬 토스 새롬 투자 계좌 (USD)
                opponent_krw_account_id = 18  # 새롬 토스 새롬 투자 계좌 (KRW)
            elif account.id == 35:  # 새롬 미래에셋 새롬 투자 계좌 (USD)
                opponent_krw_account_id = 21  # 새롬 미래에셋 새롬 투자 계좌 (KRW)

            usd_sum_in = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.account_id == account.id,
                    or_(
                        Transaction.type == TransactionType.DEPOSIT,
                        Transaction.type == TransactionType.FX_DEPOSIT,
                    ),
                )
                .scalar()
                or 0
            )

            usd_sum_out = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.account_id == account.id,
                    or_(
                        Transaction.type == TransactionType.WITHDRAWAL,
                        Transaction.type == TransactionType.FX_WITHDRAWAL,
                    ),
                )
                .scalar()
                or 0
            )
            usd_net = usd_sum_in - usd_sum_out

            krw_sum_out = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.account_id == opponent_krw_account_id,
                    Transaction.type == TransactionType.FX_WITHDRAWAL,
                )
                .scalar()
                or 0
            )

            krw_sum_in = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.account_id == opponent_krw_account_id,
                    Transaction.type == TransactionType.FX_DEPOSIT,
                )
                .scalar()
                or 0
            )

            krw_net = krw_sum_out - krw_sum_in
            print("usd_net, krw_net")
            print(usd_net, krw_net)

        account_networth = 0
        ab = AssetBreakdown()

        if account.account_type == AccountType.Checking:
            account_networth = get_checking_account_networth(db, account)
            ab += AssetBreakdown(cash=account_networth)
        elif account.account_type == AccountType.Saving:
            account_networth = get_checking_account_networth(db, account)
            ab += AssetBreakdown(saving=account_networth)
        elif account.account_type == AccountType.STOCK:
            account_networth, ab = get_stock_account_networth(db, account)
        else:
            continue

        # 프론트에서 바로 쓸 수 있도록 dict로 변환
        account_info = {
            "bank_name": account.bank_name,
            "account_name": account.account_name,
            "account_type": account.account_type.value,
            "usd_net": usd_net,
            "krw_net": krw_net,
            "breakdown": {
                "cash": float(ab.cash),
                "saving": float(ab.saving),
                "bond": float(ab.bond),
                "stock": float(ab.stock),
                "invested": float(ab.invested),
                "profit": float(ab.profit),
            },
        }

        if account.account_currency_type == AccountCurrencyType.USD:
            usd_assets_value += account_networth
            usd_accounts_data.append(account_info)
            usd_networths.append(float(account_networth))
            usd_asset_breakdown += ab
        elif account.account_currency_type == AccountCurrencyType.KRW:
            krw_assets_value += account_networth
            krw_accounts_data.append(account_info)
            krw_networths.append(float(account_networth))
            krw_asset_breakdown += ab
        print(account.account_name, ab.invested, ab.profit)

    # 4) USD/KRW 변환 계산
    total_usd = usd_assets_value + krw_assets_value / usd_krw
    total_krw = usd_assets_value * usd_krw + krw_assets_value

    usd_percent = (usd_assets_value / total_usd) * 100 if total_usd else 0
    krw_percent = (krw_assets_value / total_krw) * 100 if total_krw else 0

    total_asset_breakdown_in_usd = usd_asset_breakdown + (krw_asset_breakdown / usd_krw)

    # 5) 응답
    return {
        "rate": usd_krw,
        "as_of": as_of or datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total": {"amount_usd": total_usd, "amount_krw": total_krw},
        "breakdown": {
            "usd_assets": {
                "amount_usd": usd_assets_value,
                "amount_krw": usd_assets_value * usd_krw,
                "percent": usd_percent,
            },
            "krw_assets": {
                "amount_usd": krw_assets_value / usd_krw,
                "amount_krw": krw_assets_value,
                "percent": krw_percent,
            },
        },
        "usd_accounts": usd_accounts_data,
        "usd_networths": usd_networths,
        "krw_accounts": krw_accounts_data,
        "krw_networths": krw_networths,
        "type_breakdown": total_asset_breakdown_in_usd.to_list(),
    }
