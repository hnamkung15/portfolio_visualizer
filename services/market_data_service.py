from datetime import timedelta
import requests
import time
import FinanceDataReader as fdr
import yfinance as yf

from models.account import AssetType
from models.price import Price
from models.tickers import Ticker


def get_current_symbol_type(symbol: str):
    if symbol in [
        "US912810SN90",
        "US912810SQ22",
        "US91282CAJ09",
        "US91282CAT80",
        "US91282CBQ33",
        "157450",
        "BIL",
    ]:
        return AssetType.BOND
    return AssetType.STOCK


def get_current_symbol_price(symbol: str) -> float:
    now = time.time()

    if symbol == "Conviva":
        return 1.23
    elif symbol == "US912810SN90":  # 미국 국채 50년 5월 15일 만기
        return 4781.06 / 10
    elif symbol == "US912810SQ22":  # 미국 국채 40년 8월 15일 만기
        return 10459.28 / 17
    elif symbol == "US91282CAJ09":  # 미국 국채 25년 8월 31일 만기
        return 9993.71 / 10
    elif symbol == "US91282CAT80":  # 미국 국채 25년 10월 31일 만기
        return 9924.85 / 10
    elif symbol == "US91282CBQ33":  # 미국 국채 26년 2월 28일 만기
        return 9832.47 / 10
    elif symbol == "VFFSX":
        return 316.72
    elif symbol == "VIIIX":
        return 526.17

    if symbol.isdigit():
        symbol = f"{symbol}"

    try:
        df = fdr.DataReader(symbol)
        if not df.empty:
            price = df["Close"].iloc[-1]
            print("price found, ", symbol, ":", price)
            return float(price)
    except Exception as e:
        print(f"[WARN] FDR failed for {symbol}: {e}")

    try:
        ticker = yf.Ticker(f"{symbol}.KS")
        price = ticker.history(period="1d")["Close"].iloc[-1]
        print("price found, ", symbol, ":", price)
        return float(price)
    except Exception as e:
        print(f"[ERROR] Failed to fetch price for {symbol}: {e}")
        return 0.0


def not_searchable_symbol(symbol):
    if symbol in [
        "US912810SN90",
        "US912810SQ22",
        "US91282CAJ09",
        "US91282CAT80",
        "US91282CBQ33",
        "US91282CHD65",
        "0P0000RRID",
        "92206T105",
        "K55101DN7441",
        "SPAXX",
    ]:
        return True
    return False


price_cache = {}
tracking_symbols = {}


def price_lookup(db, symbol: str, date):
    if not symbol:
        print("[ERROR] symbol is empty", date)
        return None
    if not_searchable_symbol(symbol):
        return None

    if symbol not in tracking_symbols:
        ticker = db.query(Ticker).filter_by(symbol=symbol).first()
        if not ticker:
            ticker = Ticker(symbol=symbol)
            db.add(ticker)
            db.commit()
            db.refresh(ticker)

        prices = db.query(Price).filter(Price.ticker_id == ticker.id).all()
        price_cache[symbol] = {str(p.date): float(p.close) for p in prices}
        tracking_symbols[symbol] = ticker.id

    ticker_id = tracking_symbols[symbol]

    if symbol in price_cache and str(date) in price_cache[symbol]:
        return price_cache[symbol][str(date)]

    price = (
        db.query(Price).filter(Price.ticker_id == ticker_id, Price.date == date).first()
    )
    if price:
        return float(price.close)

    past_price = (
        db.query(Price)
        .filter(Price.ticker_id == ticker_id, Price.date < date)
        .order_by(Price.date.desc())
        .first()
    )

    future_price = (
        db.query(Price)
        .filter(Price.ticker_id == ticker_id, Price.date > date)
        .order_by(Price.date.asc())
        .first()
    )

    if past_price and future_price:
        return float(past_price.close)

    print("[market_data_service] download data ", symbol, date)
    try:
        df = fdr.DataReader(
            symbol, date - timedelta(days=60), date + timedelta(days=60)
        )
        for idx, row in df.iterrows():
            db.add(
                Price(
                    ticker_id=ticker_id,
                    date=idx.date(),
                    close=row["Close"],
                    open=row.get("Open"),
                    high=row.get("High"),
                    low=row.get("Low"),
                    volume=row.get("Volume"),
                )
            )
        db.commit()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {symbol} from FDR: {e}")

    price = (
        db.query(Price)
        .filter(Price.ticker_id == ticker_id, Price.date <= date)
        .order_by(Price.date.desc())
        .first()
    )
    return float(price.close) if price else None


# df = fdr.DataReader("VIIIX", "2025-09-01", "2025-09-10")
# print(df)
