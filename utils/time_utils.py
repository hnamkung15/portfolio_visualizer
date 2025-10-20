"""
Time utility functions for consistent timezone handling across the application.
"""

from datetime import datetime, timedelta, date
import pytz


# KST timezone
KST = pytz.timezone("Asia/Seoul")
PT = pytz.timezone("US/Pacific")


def get_kst_now() -> datetime:
    """Get current datetime in KST timezone."""
    return datetime.now(KST)


def get_kst_today() -> date:
    """Get current date in KST timezone."""
    return get_kst_now().date()


def get_kst_yesterday() -> date:
    """Get yesterday's date in KST timezone."""
    return get_kst_today() - timedelta(days=1)


def get_pt_now() -> datetime:
    """Get current datetime in Pacific timezone (PST/PDT)."""
    return datetime.now(PT)


def get_pt_today() -> date:
    """Get current date in Pacific timezone (PST/PDT)."""
    return get_pt_now().date()


def get_pt_yesterday() -> date:
    """Get yesterday's date in Pacific timezone (PST/PDT)."""
    return get_pt_today() - timedelta(days=1)


def is_weekend(date_obj: date) -> bool:
    """Check if a date is weekend (Saturday or Sunday)."""
    return date_obj.weekday() in (5, 6)


def active_date_until() -> date:
    """
    Return the latest date for which the U.S. stock market closing price is valid.

    Logic:
    - If the current time in Pacific Time (PT) is past 1:00 PM (equivalent to 4:00 PM ET),
      then today's closing price is active → return today's date (PT).
    - Otherwise, the market has not yet closed today → return yesterday's date (PT).

    This helps determine which trading day's closing price should be considered "active".
    """
    now = get_pt_now()
    market_close_time = now.replace(hour=13, minute=0, second=0, microsecond=0)

    if now >= market_close_time:
        return get_pt_today()
    else:
        return get_pt_yesterday()


def str_to_date(d: str) -> date:
    """'YYYY-MM-DD' 문자열을 date 객체로 변환"""
    return datetime.strptime(d, "%Y-%m-%d").date()


def is_consecutive_weekend(start_date: str, end_date: str) -> bool:
    """
    Check if both start_date and end_date (given as 'YYYY-MM-DD' strings) are weekends,
    and they are consecutive days (e.g., Saturday ~ Sunday).
    """
    s_date = str_to_date(start_date)
    e_date = str_to_date(end_date)

    if is_weekend(s_date) and is_weekend(e_date):
        return (e_date - s_date).days <= 1
    return False
