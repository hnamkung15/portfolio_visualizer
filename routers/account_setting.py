from fastapi import APIRouter, Request, Form, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from db import get_db
from routers.auth import get_current_user
from models.user import User

from models.account import (
    Account,
    AccountCategory,
    AccountCountry,
    AccountCurrencyType,
    AccountType,
    BankName,
    Owner,
)
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/account_setting", response_class=HTMLResponse)
def account_setting(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).order_by(Account.order).all()
    return templates.TemplateResponse(
        "account_setting/accounts.html",
        {
            "request": request,
            "accounts": accounts,
            "active": "account_setting",
            "bank_names": list(BankName),
            "owners": list(Owner),
            "account_countries": [AccountCountry.US, AccountCountry.KOR],
            "account_currency_types": list(AccountCurrencyType),
            "account_types": list(AccountType),
            "account_categories": list(AccountCategory),
        },
    )


@router.get("/account_setting/add")
def add_account_page(request: Request):
    """Redirect to account setting page for adding accounts."""
    return RedirectResponse(url="/account_setting", status_code=302)


@router.post("/account_setting/add")
def add_account(
    request: Request,
    owner: Owner = Form(...),
    bank_name: BankName = Form(...),
    account_name: str = Form(...),
    account_currency_type: AccountCurrencyType = Form(...),
    account_type: AccountType = Form(...),
    account_category: AccountCategory = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    max_order = db.query(Account).count()
    new_acc = Account(
        owner=owner,
        bank_name=bank_name,
        account_name=account_name,
        account_currency_type=account_currency_type,
        account_type=account_type,
        account_category=account_category,
        order=max_order,
        user_id=current_user.id,
    )
    db.add(new_acc)
    db.commit()
    return RedirectResponse(url="/account_setting", status_code=303)


@router.post("/account_setting/delete/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    acc = db.query(Account).filter(Account.user_id == current_user.id, Account.id == account_id).first()
    if acc:
        db.delete(acc)
        db.commit()
    return RedirectResponse(url="/account_setting", status_code=303)


@router.post("/account_setting/reorder")
def reorder_accounts(data: dict = Body(...), db: Session = Depends(get_db)):
    order = data["order"]
    for i, acc_id in enumerate(order):
        account = db.query(Account).filter_by(id=int(acc_id)).first()
        if account:
            account.order = i
    db.commit()
    return {"status": "ok"}


@router.post("/account_setting/update/{account_id}")
def update_account(
    account_id: int,
    owner: Owner = Form(...),
    bank_name: BankName = Form(...),
    account_name: str = Form(...),
    account_country: AccountCountry = Form(...),
    account_currency_type: AccountCurrencyType = Form(...),
    account_type: AccountType = Form(...),
    account_category: AccountCategory = Form(...),
    db: Session = Depends(get_db),
):
    acc = db.query(Account).get(account_id)
    if not acc:
        return RedirectResponse(url="/account_setting", status_code=404)

    acc.owner = owner
    acc.bank_name = bank_name
    acc.account_name = account_name
    acc.account_country = account_country
    acc.account_currency_type = account_currency_type
    acc.account_type = account_type
    acc.account_category = account_category

    db.commit()
    return RedirectResponse(url="/account_setting", status_code=303)
