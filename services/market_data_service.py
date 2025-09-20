from datetime import timedelta, datetime
import time
import FinanceDataReader as fdr
import yfinance as yf

from models.account import AssetType
from models.price import Price
from models.tickers import Ticker
from utils.time_utils import get_kst_yesterday


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


def download_ticker_data(db, ticker, start_date, end_date):
    symbol = ticker.symbol
    print(
        f"[market_data_service] download data for {symbol} from starting date ({start_date}) to yesterday ({end_date})"
    )
    try:
        df = fdr.DataReader(symbol, str(start_date), str(end_date))
        for idx, row in df.iterrows():
            db.add(
                Price(
                    ticker_id=ticker.id,
                    date=idx.date(),
                    close=row["Close"],
                    open=row.get("Open"),
                    high=row.get("High"),
                    low=row.get("Low"),
                    volume=row.get("Volume"),
                )
            )

        # Update last_data_sync timestamp to yesterday (the last date we downloaded)
        ticker.last_data_sync = end_date
        db.commit()
        print(
            f"[market_data_service] Successfully backfilled {len(df)} records for {symbol}"
        )
        return ticker
    except Exception as e:
        print(f"[ERROR] Failed to backfill {symbol} from FDR: {e}")
        return None


data_starting_date = "2020-01-02"

price_cache = {}
tracking_symbols = {}
last_syncup_time = {}


def load_ticker_into_cache(db, symbol: str, ticker):
    prices = db.query(Price).filter(Price.ticker_id == ticker.id).all()
    price_cache[symbol] = {str(p.date): float(p.close) for p in prices}
    tracking_symbols[symbol] = ticker.id
    last_syncup_time[symbol] = ticker.last_data_sync


# This function is not supposed to return realtime price,
# it only designed to return historical data. If date happens
# to be the closed market date (e.g., weekends or holidays),
# then return previous date data.


def price_lookup(db, symbol: str, date):
    if not symbol:
        print("[ERROR] symbol is empty", date)
        return None
    if not_searchable_symbol(symbol):
        return None

    yesterday = get_kst_yesterday()

    if date > yesterday:
        return None

    # Ensure cache data for ticker is loaded.
    # We can check this by looking into tracking_tickers
    if symbol not in tracking_symbols:
        ticker = db.query(Ticker).filter_by(symbol=symbol).first()

        # If symbol is not in Ticker table, it means, this is the first time
        # seeing this symbol. We need to backfill data.
        if not ticker:
            ticker = Ticker(symbol=symbol)
            db.add(ticker)
            db.commit()
            db.refresh(ticker)
            ticker = download_ticker_data(db, ticker, data_starting_date, yesterday)

        load_ticker_into_cache(db, symbol, ticker)

    if last_syncup_time[symbol] < yesterday:
        ticker = download_ticker_data(
            db, ticker, last_syncup_time[symbol] + timedelta(days=1), yesterday
        )
        load_ticker_into_cache(db, symbol, ticker)

    if str(date) in price_cache[symbol]:
        return price_cache[symbol][str(date)]

    ticker_id = tracking_symbols[symbol]
    past_price = (
        db.query(Price)
        .filter(Price.ticker_id == ticker_id, Price.date < date)
        .order_by(Price.date.desc())
        .first()
    )
    return past_price
