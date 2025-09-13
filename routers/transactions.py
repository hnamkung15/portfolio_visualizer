from fastapi import APIRouter, File, Form, Depends, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db
from models.account import Account
from models.transactions import Transaction, TransactionType
from datetime import date
from typing import Optional
from i18n_helpers import get_templates_with_i18n

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/transactions", response_class=HTMLResponse)
def view_transactions(
    request: Request,
    account_id: int = None,
    db: Session = Depends(get_db),
):
    accounts = db.query(Account).order_by(Account.order).all()
    transactions = []
    selected_account = None
    latest_type = ""
    latest_date = ""

    if account_id:
        selected_account = db.query(Account).get(account_id)
        transactions = (
            db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .order_by(Transaction.date.asc(), Transaction.id.asc())
            .all()
        )

        if transactions:
            latest_type = transactions[-1].type
            latest_date = transactions[-1].date.isoformat()

        transactions.sort(key=lambda t: (t.date, t.id), reverse=True)

    i18n_templates = get_templates_with_i18n(request)
    return i18n_templates.TemplateResponse(
        "transactions/transactions.html",
        {
            "request": request,
            "accounts": accounts,
            "active": "transactions",
            "transactions": transactions,
            "selected_account": selected_account,
            "transaction_types": list(TransactionType),
            "transaction_type_map": {
                name: member.value
                for name, member in TransactionType.__members__.items()
            },
            "latest_type": latest_type,
            "latest_date": latest_date,
        },
    )


@router.post("/transactions/add")
def add_transaction(
    date: date = Form(...),
    account_id: int = Form(...),
    amount: float = Form(...),
    type: TransactionType = Form(...),
    description: Optional[str] = Form(None),
    symbol: Optional[str] = Form(None),
    fx_rate: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    fee: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    parsed_fx_rate = float(fx_rate) if fx_rate and fx_rate.strip() != "" else None
    parsed_price = float(price) if price and price.strip() != "" else None
    parsed_quantity = float(quantity) if quantity and quantity.strip() != "" else None
    parsed_fee = float(fee) if fee and fee.strip() != "" else None

    new_tx = Transaction(
        date=date,
        account_id=account_id,
        amount=amount,
        type=type,
        description=description,
        symbol=symbol,
        fx_rate=parsed_fx_rate,
        price=parsed_price,
        quantity=parsed_quantity,
        fee=parsed_fee,
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    return JSONResponse({"status": "ok"})


@router.post("/transactions/delete/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).get(tx_id)
    if tx:
        account_id = tx.account_id
        db.delete(tx)
        db.commit()
        return RedirectResponse(
            url=f"/transactions?account_id={account_id}", status_code=303
        )
    return RedirectResponse(url="/transactions", status_code=404)


@router.post("/transactions/update/{tx_id}")
def update_transaction(
    tx_id: int,
    date: date = Form(...),
    amount: float = Form(...),
    type: TransactionType = Form(...),
    symbol: Optional[str] = Form(None),
    fx_rate: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    fee: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    tx = db.query(Transaction).get(tx_id)
    if not tx:
        return RedirectResponse(url="/transactions", status_code=404)

    tx.date = date
    tx.amount = amount
    tx.type = type
    tx.symbol = symbol
    tx.description = description
    tx.fx_rate = float(fx_rate) if fx_rate and fx_rate.strip() else None
    tx.price = float(price) if price and price.strip() else None
    tx.quantity = float(quantity) if quantity and quantity.strip() else None
    tx.fee = float(fee) if fee and fee.strip() else None

    db.commit()

    return RedirectResponse(
        url=f"/transactions?account_id={tx.account_id}", status_code=303
    )


@router.post("/transactions/upload_csv")
async def upload_csv(
    account_id: int = Form(...),
    csv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # import pandas as pd
    # from io import StringIO
    # from datetime import datetime

    # contents = await csv_file.read()
    # df = pd.read_csv(StringIO(contents.decode("utf-8")))
    # print(df)

    if account_id == 16:  # Fidelity Stock Account
        db.query(Transaction).filter(Transaction.account_id == account_id).delete()
        db.commit()

        import pandas as pd
        from io import StringIO
        from datetime import datetime

        contents = await csv_file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))

        def parse_date(s):
            return datetime.strptime(s.strip(), "%m/%d/%Y").date()

        def parse_amount(row):
            amt = row.get("Amount ($)", 0)
            if pd.isna(amt):
                return 0
            return float(amt)

        def map_type(action):
            if "ACCTVERIFY" in action or "REINVESTMENT" in action:
                return None
            if "Electronic Funds Transfer Received (Cash)" in action:
                return TransactionType.DEPOSIT
            if "Electronic Funds Transfer Paid (Cash)" in action:
                return TransactionType.WITHDRAWAL
            if "YOU BOUGHT" in action:
                return TransactionType.BUY
            if "YOU SOLD" in action:
                return TransactionType.SELL
            if "DIVIDEND" in action:
                return TransactionType.DIVIDEND
            if "REINVESTMENT" in action or "INTEREST" in action:
                return TransactionType.INTEREST
            return None

        for _, row in df.iloc[::-1].iterrows():
            type = map_type(row["Action"])
            if type != None:
                parsed_quantity = row.get("Quantity", None)
                tx = Transaction(
                    date=parse_date(row["Run Date"]),
                    account_id=account_id,
                    type=type,
                    amount=abs(parse_amount(row)),
                    symbol=row.get("Symbol", ""),
                    description="",
                    price=row.get("Price ($)", None),
                    quantity=(
                        abs(parsed_quantity) if parsed_quantity is not None else None
                    ),
                    fee=row.get("Fees ($)", None),
                    fx_rate=None,
                )
                db.add(tx)
        db.commit()

    return RedirectResponse(
        url=f"/transactions?account_id={account_id}", status_code=303
    )
