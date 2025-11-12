from datetime import timedelta, datetime
import time
import FinanceDataReader as fdr
import yfinance as yf

from models.account import AssetType
from models.price import Price
from models.tickers import Ticker
from utils.time_utils import (
    get_pt_yesterday,
    is_consecutive_weekend,
    str_to_date,
    active_date_until,
)


def get_current_symbol_type(symbol: str):
    if symbol in [
        "US912810SN90",
        "US912810SQ22",
        "US91282CAJ09",
        "US91282CAT80",
        "US91282CBQ33",
        "157450",
        "BIL",
        "SGOV",
    ]:
        return AssetType.BOND
    return AssetType.STOCK


def get_current_symbol_price(symbol: str, db) -> float:
    if symbol == "Conviva":
        return 1.23
    elif symbol == "US912810SN90":  # 미국 국채 50년 5월 15일 만기
        # return 4935.13 / 10
        return 5073.75 / 10
    elif symbol == "US912810SQ22":  # 미국 국채 40년 8월 15일 만기
        # return 10735.57 / 17
        return 10925.48 / 17
    elif symbol == "US91282CAJ09":  # 미국 국채 25년 8월 31일 만기
        return 9993.71 / 10
    elif symbol == "US91282CAT80":  # 미국 국채 25년 10월 31일 만기
        # return 9969.59 / 10
        return 9994.58 / 10
    elif symbol == "US91282CBQ33":  # 미국 국채 26년 2월 28일 만기
        # return 9857.82 / 10
        return 9882.45

    if symbol.isdigit():
        symbol = f"{symbol}"

    yesterday = get_pt_yesterday()
    price = price_lookup(db, symbol, yesterday)
    if price:
        return price
    return 0


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
        "Conviva",
    ]:
        return True
    return False


# We use last_data_sync, not for last date data in price, but last "trial"
# of requesting data.


def download_ticker_data(db, ticker, start_date, end_date):
    symbol = ticker.symbol

    start_date_date = str_to_date(str(start_date))
    end_date_date = str_to_date(str(end_date))

    if is_consecutive_weekend(str(start_date), str(end_date)):
        print(
            f"[market_data_service] During {start_date} ~ {end_date} for {symbol}, skipped (consecutive weekend)"
        )
    else:
        try:
            df = fdr.DataReader(
                symbol, str(start_date), str(end_date + timedelta(days=1))
            )
            df = df[
                (df.index.date >= start_date_date) & (df.index.date <= end_date_date)
            ]
            if len(df) > 0:
                for idx, row in df.iterrows():
                    date_val = idx.date()

                    exists = (
                        db.query(Price)
                        .filter(Price.ticker_id == ticker.id, Price.date == date_val)
                        .first()
                    )

                    if not exists:
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
                print(
                    f"[market_data_service] During {start_date} ~ {end_date} for {symbol}, downloaded ({len(df)}) records"
                )
            else:
                print(
                    f"[market_data_service] During {start_date} ~ {end_date} for {symbol}, there is no record"
                )
        except Exception as e:
            print(
                f"[Error] data download failed during {start_date} ~ {end_date} for {symbol}: {e}"
            )
        ticker.last_data_sync = end_date
        db.commit()

    return ticker


data_starting_date = "2020-01-02"

price_cache = {}
tracking_symbols = {}
last_syncup_time = {}


def load_ticker_into_cache(db, symbol: str, ticker):
    prices = db.query(Price).filter(Price.ticker_id == ticker.id).all()
    price_cache[symbol] = {str(p.date): float(p.close) for p in prices}
    tracking_symbols[symbol] = ticker.id
    last_syncup_time[symbol] = ticker.last_data_sync


def ensure_symbol_in_cache(db, symbol: str, active_date):
    """
    심볼이 캐시에 없는 경우:
    - DB에서 ticker를 찾고
    - 없으면 새로 생성 및 백필(backfill)
    - 캐시에 적재
    """
    if symbol not in tracking_symbols:
        ticker = db.query(Ticker).filter_by(symbol=symbol).first()

        if not ticker:
            ticker = Ticker(symbol=symbol)
            db.add(ticker)
            db.commit()
            db.refresh(ticker)

            # 최초 백필: 시작일 ~ 오늘
            ticker = download_ticker_data(db, ticker, data_starting_date, active_date)

        load_ticker_into_cache(db, symbol, ticker)


def sync_symbol_if_needed(db, symbol: str, active_date):
    """
    심볼이 캐시에 있지만, 최신 데이터가 아닌 경우:
    - 마지막 동기화 시점 이후부터 오늘까지 증분 업데이트
    - 캐시 갱신
    """
    last_sync = last_syncup_time.get(symbol)

    if last_sync is None or last_sync < active_date:
        ticker = db.query(Ticker).filter_by(symbol=symbol).first()
        last_price = (
            db.query(Price)
            .filter(Price.ticker_id == ticker.id)
            .order_by(Price.date.desc())
            .first()
        )

        start_date = (
            last_price.date + timedelta(days=1) if last_price else data_starting_date
        )

        ticker = db.query(Ticker).filter_by(symbol=symbol).first()
        ticker = download_ticker_data(db, ticker, start_date, active_date)
        load_ticker_into_cache(db, symbol, ticker)


# This function is not supposed to return realtime price,
# it only designed to return historical data. If date happens
# to be the closed market date (e.g., weekends or holidays),
# then return previous date data.
def price_lookup(db, symbol: str, date):
    if not symbol:
        print("[ERROR] symbol is empty", date)
        return None
    if not_searchable_symbol(symbol):
        if symbol == "US912810SN90":  # 미국 국채 50년 5월 15일 만기
            # return 4935.13 / 10
            return 5073.75 / 10
        elif symbol == "US912810SQ22":  # 미국 국채 40년 8월 15일 만기
            # return 10735.57 / 17
            return 10925.48 / 17
        elif symbol == "US91282CAJ09":  # 미국 국채 25년 8월 31일 만기
            return 9993.71 / 10
        elif symbol == "US91282CAT80":  # 미국 국채 25년 10월 31일 만기
            # return 9969.59 / 10
            return 9994.58 / 10
        elif symbol == "US91282CBQ33":  # 미국 국채 26년 2월 28일 만기
            # return 9857.82 / 10
            return 9882.45 / 10
        print("[Warning] not_searchable_symbol", symbol, date)

        return None

    active_date = active_date_until()
    # active_date = get_pt_yesterday()

    if active_date < date:
        return None

    # print("price_lookup", symbol, date)

    # below 2 functions are irrelevant to "date" value
    # based on active_date, these functions try to make price data
    # up to date.
    ensure_symbol_in_cache(db, symbol, active_date)
    sync_symbol_if_needed(db, symbol, active_date)

    if str(date) in price_cache[symbol]:
        return price_cache[symbol][str(date)]

    ticker_id = tracking_symbols[symbol]
    past_price = (
        db.query(Price)
        .filter(Price.ticker_id == ticker_id, Price.date < date)
        .order_by(Price.date.desc())
        .first()
    )
    if past_price:
        print(
            f"[Warning] use past data for {symbol}, {date} is requested, but {past_price.date} is returned"
        )
        return float(past_price.close)
    print("[Error] no data?", symbol, date)
    return None


# df = fdr.DataReader("VFFSX", "2025-11-1", "2025-11-12")
# print(df)

# df = fdr.DataReader("USD/KRW", "2025-09-26", "2025-09-26")
# print(df)

# df = fdr.DataReader("GOOG", "2025-10-01", "2025-11-07")
# print(df)

# df = fdr.DataReader("GOOG", "2025-10-01", "2025-11-12")
# print(df)
