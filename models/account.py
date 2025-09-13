from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum
from models.base import Base
from dataclasses import dataclass


# --- ENUM TYPES ---
class BankName(str, enum.Enum):
    # 미국 은행 및 기관
    CHASE = "Chase"
    VANGUARD = "Vanguard"
    PNC = "PNC"
    CHARLES_SCHWAB = "Charles Schwab"
    Fidelity = "Fidelity"
    CARTA = "Carta"
    HEALTH_EQUITY = "Health Equity"
    UMB = "UMB"

    # 한국 은행 및 기관
    TOSS = "토스"
    MIRAE_ASSET = "미래에셋"
    SHINHAN = "신한은행"
    KB = "국민은행"
    SHINHYUP = "신협"
    NONGHYUP = "농협"
    BNK = "경남은행"
    KSTECH = "과학기술인공제회"


class AccountCountry(str, enum.Enum):
    US = "US"
    KOR = "KOR"


class AccountCurrencyType(str, enum.Enum):
    USD = "USD"
    KRW = "KRW"


class AccountType(str, enum.Enum):
    Checking = "Checking"
    Saving = "Saving"
    STOCK = "Stock"  # stock account


class Owner(str, enum.Enum):
    HUN = "훈"
    SAEROM = "새롬"
    YUEL = "유엘"


class AccountCategory(str, enum.Enum):
    PERSONAL = "개인 계좌"
    KOR_PSA = "한국 연금 저축"
    KOR_IRP = "한국 개인형 퇴직 연금"
    KOR_PENSION = "한국 연금"

    US_401k = "401k"
    US_401k_PRETAX = "PreTax 401k"
    US_401k_ROTH = "Roth 401k"
    US_401k_AFTERTAX = "AfterTax 401k"
    US_ROTH_IRA = "Roth IRA"
    HSA = "HSA"
    RSU = "주식 보상 계좌 (RSU)"


class AssetType(str, enum.Enum):
    CASH = "cash"
    SAVING = "saving"
    BOND = "bond"
    STOCK = "stock"


@dataclass
class AssetBreakdown:
    cash: float = 0
    saving: float = 0
    bond: float = 0
    stock: float = 0
    invested: float = 0
    profit: float = 0

    def __add__(self, other: "AssetBreakdown") -> "AssetBreakdown":
        return AssetBreakdown(
            cash=self.cash + other.cash,
            saving=self.saving + other.saving,
            bond=self.bond + other.bond,
            stock=self.stock + other.stock,
            invested=self.invested + other.invested,
            profit=self.profit + other.profit,
        )

    def __mul__(self, scalar: float) -> "AssetBreakdown":
        return AssetBreakdown(
            cash=self.cash * scalar,
            saving=self.saving * scalar,
            bond=self.bond * scalar,
            stock=self.stock * scalar,
            invested=self.invested * scalar,
            profit=self.profit * scalar,
        )

    def __truediv__(self, scalar):
        return AssetBreakdown(
            self.cash / scalar,
            self.saving / scalar,
            self.bond / scalar,
            self.stock / scalar,
            self.invested / scalar,
            self.profit / scalar,
        )

    def to_list(self):
        return [
            self.cash,
            self.saving,
            self.bond,
            self.stock,
            self.invested,
            self.profit,
        ]


# --- ACCOUNT MODEL ---
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    order = Column(Integer, default=0)

    owner = Column(Enum(Owner), nullable=False)
    bank_name = Column(Enum(BankName), nullable=False)
    account_name = Column(String, nullable=False)
    account_country = Column(
        Enum(AccountCountry),
        nullable=False,
        server_default="US",
        default=AccountCountry.US,
    )
    account_currency_type = Column(Enum(AccountCurrencyType), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_category = Column(Enum(AccountCategory), nullable=False)

    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete"
    )
