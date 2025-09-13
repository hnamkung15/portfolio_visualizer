from sqlalchemy.orm import declarative_base

Base = declarative_base()


# class AssetType(str, enum.Enum):
#     CASH = "현금"
#     STABLE = "안정 자산"
#     EQUITY = "주식"


# class Currency(str, enum.Enum):
#     KRW = "KRW"
#     USD = "USD"


# class Liquidity(str, enum.Enum):
#     LIQUID = "Liquid"  # 일반 계좌
#     LOCKED = "Locked"  # 연금계좌 (e.g., 401k)
