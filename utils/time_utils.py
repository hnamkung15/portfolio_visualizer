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
