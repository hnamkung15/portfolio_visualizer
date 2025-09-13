from sqlalchemy import Column, Integer, Numeric, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models.base import Base


class TransactionType(str, enum.Enum):
    DEPOSIT = "입금"
    WITHDRAWAL = "출금"
    FX_DEPOSIT = "외환 입금"
    FX_WITHDRAWAL = "외환 출금"

    INTEREST = "이자 지급"
    DIVIDEND = "배당금 지급"
    BUY = "주식 구입"
    SELL = "주식 판매"
    VESTING = "주식 수여"
    FX = "환전"
    BALANCE_SNAPSHOT = "현재 잔고"
    TAX_FEE = "세금 or 수수료"


# --- TRANSACTION MODEL ---
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    symbol = Column(String(20), nullable=True)
    fx_rate = Column(Numeric(precision=12, scale=6), nullable=True)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    price = Column(Numeric(precision=12, scale=2), nullable=True)
    quantity = Column(Numeric(precision=12, scale=4), nullable=True)
    fee = Column(Numeric(precision=12, scale=2), nullable=True)
    description = Column(String, nullable=True)

    account = relationship("Account", back_populates="transactions")
