from models.account import AccountCategory, AccountType
from models.transactions import Transaction, TransactionType


def annotate_with_balances(transactions, account):
    if account.account_type == AccountType.Saving:
        running_balance = 0
        for tx in sorted(transactions, key=lambda t: (t.date, t.id)):
            if tx.type in [TransactionType.DEPOSIT, TransactionType.INTEREST]:
                running_balance += tx.amount
            elif tx.type == TransactionType.WITHDRAWAL:
                running_balance -= tx.amount
            tx.balance = running_balance
        return running_balance if transactions else 0

    if account.account_type == AccountType.STOCK:
        if account.account_category == AccountCategory.RSU:
            running_quantity = 0
            for tx in sorted(transactions, key=lambda t: (t.date, t.id)):
                qty = tx.quantity or 0

                if tx.type in [TransactionType.VESTING]:
                    running_quantity += qty

                tx.balance = running_quantity
            return 0
        running_balance = 0
        for tx in sorted(transactions, key=lambda t: (t.date, t.id)):
            if tx.type in [
                TransactionType.DEPOSIT,
                TransactionType.FX_DEPOSIT,
                TransactionType.INTEREST,
                TransactionType.DIVIDEND,
                TransactionType.SELL,
            ]:
                running_balance += tx.amount
            elif tx.type in [
                TransactionType.WITHDRAWAL,
                TransactionType.FX_WITHDRAWAL,
                TransactionType.BUY,
                TransactionType.TAX_FEE,
            ]:
                running_balance -= tx.amount
            tx.balance = running_balance
        return running_balance if transactions else 0


def annotate_with_quantities_by_symbol(transactions, account):
    if account.account_type != AccountType.STOCK:
        return {}

    symbol_info_map = {}

    if account.account_category == AccountCategory.RSU:
        for tx in sorted(transactions, key=lambda t: (t.date, t.id)):
            symbol = tx.symbol
            if not symbol:
                continue

            if symbol not in symbol_info_map:
                symbol_info_map[symbol] = {"quantity": 0, "cost_basis": 0.0}

            qty = float(tx.quantity or 0)
            if tx.type == TransactionType.VESTING:
                vest_price = float(tx.price or 0)
                symbol_info_map[symbol]["quantity"] += qty
                symbol_info_map[symbol]["cost_basis"] += vest_price * qty

    else:
        for tx in sorted(transactions, key=lambda t: (t.date, t.id)):
            symbol = tx.symbol
            if not symbol:
                tx.quantity_balance = None
                continue

            if symbol not in symbol_info_map:
                symbol_info_map[symbol] = {"quantity": 0, "cost_basis": 0.0}

            qty = float(tx.quantity or 0)
            price = float(tx.price or 0.0)

            if tx.type == TransactionType.BUY:
                symbol_info_map[symbol]["quantity"] += qty
                symbol_info_map[symbol]["cost_basis"] += price * qty
            elif tx.type == TransactionType.SELL:
                if symbol_info_map[symbol]["quantity"] > 0:
                    avg_price = (
                        symbol_info_map[symbol]["cost_basis"]
                        / symbol_info_map[symbol]["quantity"]
                    )
                    symbol_info_map[symbol]["cost_basis"] -= avg_price * qty
                symbol_info_map[symbol]["quantity"] -= qty

            tx.quantity_balance = symbol_info_map[symbol]["quantity"]

    return symbol_info_map
