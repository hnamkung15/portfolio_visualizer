# models/tickers.py
from sqlalchemy import Column, Date, Integer, String
from models.base import Base


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False)  # 예: "SCHD", "VOO"
    name = Column(String(100), nullable=True)  # ETF/주식 풀네임
    exchange = Column(String(50), nullable=True)  # 거래소 (NYSE, NASDAQ 등)
    currency = Column(String(10), nullable=True)  # USD, KRW 등
    last_data_sync = Column(Date, nullable=True)
