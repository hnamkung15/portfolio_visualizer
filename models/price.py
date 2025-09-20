# models/price.py
from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    date = Column(Date, nullable=True)
    close = Column(Numeric(precision=12, scale=4), nullable=True)
    open = Column(Numeric(precision=12, scale=4), nullable=True)
    high = Column(Numeric(precision=12, scale=4), nullable=True)
    low = Column(Numeric(precision=12, scale=4), nullable=True)
    volume = Column(Numeric(precision=20, scale=2), nullable=True)

    ticker = relationship("Ticker", backref="prices")


class RealTimePrice(Base):
    __tablename__ = "realtime_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey("tickers.id"), nullable=False)
    price = Column(Numeric(precision=12, scale=4), nullable=True)

    ticker = relationship("Ticker", backref="realtime_prices")
