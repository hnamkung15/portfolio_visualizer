from collections import defaultdict
from sqlalchemy.orm import Session
from models.account import Account, AssetBreakdown, AssetType
from models.transactions import Transaction, TransactionType
from services.market_data_service import (
    get_current_symbol_price,
    get_current_symbol_type,
)
from services.transaction_service import (
    annotate_with_balances,
    annotate_with_quantities_by_symbol,
)


def get_checking_account_networth(db: Session, account: Account) -> float:
    latest_snapshot = (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account.id,
            Transaction.type == TransactionType.BALANCE_SNAPSHOT,
        )
        .order_by(Transaction.date.desc())  # 최신 날짜 기준
        .first()
    )

    if latest_snapshot:
        return float(latest_snapshot.amount)
    return 0.0


def get_stock_account_networth(db: Session, account: Account) -> float:
    transactions = (
        db.query(Transaction).filter(Transaction.account_id == account.id).all()
    )

    if not transactions:
        return 0.0

    latest_balance = float(annotate_with_balances(transactions, account))
    portfolio = annotate_with_quantities_by_symbol(transactions, account)
    ab = AssetBreakdown(cash=latest_balance)

    dividends_by_symbol = defaultdict(float)
    for t in transactions:
        if t.type == TransactionType.DIVIDEND and t.symbol:
            dividends_by_symbol[t.symbol] += float(t.amount)

    for symbol, info in portfolio.items():
        quantity = info["quantity"]
        cost_basis = info["cost_basis"]

        if abs(quantity) < 1e-6:
            continue

        price = get_current_symbol_price(symbol)
        valuation = price * quantity
        dividend = dividends_by_symbol.get(symbol, 0.0)
        profit = valuation - cost_basis + dividend

        latest_balance += valuation
        symbol_type = get_current_symbol_type(symbol)

        if symbol_type == AssetType.BOND:
            ab += AssetBreakdown(bond=valuation, invested=cost_basis, profit=profit)
        elif symbol_type == AssetType.STOCK:
            ab += AssetBreakdown(stock=valuation, invested=cost_basis, profit=profit)
        else:
            print("ERROR! shouldn't come here")

    return float(latest_balance), ab
