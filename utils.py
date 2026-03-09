# utils.py
# Utility / helper functions — validation, formatting, etc.

from datetime import datetime


def validate_amount(amount_str: str) -> float | None:
    """
    Validate and convert an amount string to float.
    Returns the float if valid, None otherwise.
    """
    try:
        value = float(amount_str.strip())
        if value <= 0:
            return None
        return round(value, 2)
    except ValueError:
        return None


def validate_date(date_str: str) -> bool:
    """
    Check if a date string is in YYYY-MM-DD format and is a real date.
    """
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_title(title: str) -> bool:
    """Title must be non-empty and under 100 characters."""
    return 0 < len(title.strip()) <= 100


def format_currency(amount: float) -> str:
    """Format a float as Indian Rupee string."""
    return f"₹{amount:,.2f}"


def format_month_label(yyyy_mm: str) -> str:
    """Convert '2024-05' → 'May 2024' for chart labels."""
    try:
        dt = datetime.strptime(yyyy_mm, "%Y-%m")
        return dt.strftime("%b %Y")
    except ValueError:
        return yyyy_mm


def get_current_year_month() -> tuple:
    """Return (year, month) as integers for the current month."""
    now = datetime.now()
    return now.year, now.month
