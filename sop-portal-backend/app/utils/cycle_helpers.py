"""
S&OP Cycle Helper Utilities
Functions for calculating planning periods, cycle dates, etc.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any


def calculate_16_month_period(start_date: datetime = None) -> Dict[str, Any]:
    """
    Calculate 16-month planning period from a given start date
    Returns dict with start month, end month, and list of all months

    The 16-month period typically includes:
    - Last 4 months (historical for reference)
    - Current month
    - Next 11 months (forecast period)
    """
    if start_date is None:
        start_date = datetime.now()

    # Start from 4 months ago (for historical context)
    period_start = start_date - relativedelta(months=4)

    # End 11 months in the future (total 16 months)
    period_end = start_date + relativedelta(months=11)

    # Generate list of all months in the period
    months = []
    current_month = period_start.replace(day=1)

    while current_month <= period_end:
        months.append({
            "year": current_month.year,
            "month": current_month.month,
            "monthLabel": current_month.strftime("%Y-%m"),
            "monthName": current_month.strftime("%B %Y"),
            "isHistorical": current_month < start_date.replace(day=1),
            "isCurrent": current_month.year == start_date.year and current_month.month == start_date.month,
            "isFuture": current_month > start_date.replace(day=1)
        })
        current_month = current_month + relativedelta(months=1)

    return {
        "startYear": period_start.year,
        "startMonth": period_start.month,
        "endYear": period_end.year,
        "endMonth": period_end.month,
        "totalMonths": len(months),
        "months": months,
        "periodLabel": f"{period_start.strftime('%Y-%m')} to {period_end.strftime('%Y-%m')}"
    }


def get_current_cycle_period() -> Dict[str, Any]:
    """
    Get the current cycle's 16-month period
    Based on current date
    """
    return calculate_16_month_period(datetime.now())


def is_date_in_period(check_date: datetime, period: Dict[str, Any]) -> bool:
    """
    Check if a given date falls within a planning period
    """
    check_year = check_date.year
    check_month = check_date.month

    start_year = period["startYear"]
    start_month = period["startMonth"]
    end_year = period["endYear"]
    end_month = period["endMonth"]

    if check_year < start_year or check_year > end_year:
        return False

    if check_year == start_year and check_month < start_month:
        return False

    if check_year == end_year and check_month > end_month:
        return False

    return True


def generate_cycle_name(start_date: datetime = None) -> str:
    """
    Generate a standard cycle name based on the period
    Format: "S&OP Cycle YYYY-MM"
    """
    if start_date is None:
        start_date = datetime.now()

    return f"S&OP Cycle {start_date.strftime('%Y-%m')}"


def calculate_submission_deadline(cycle_start: datetime, days_before_end: int = 7, cycle_end: datetime | None = None) -> datetime:
    """
    Calculate submission deadline.
    Prefer provided cycle_end (dates.endDate) when available, otherwise derive from cycle_start.
    The deadline is set to 23:59:59 of (cycle_end - days_before_end).
    """
    # Prefer explicit end date
    if cycle_end is None:
        # Derive end as the last day of the start month
        derived_end = (cycle_start.replace(day=28) + relativedelta(days=4))  # next month
        derived_end = derived_end.replace(day=1) - relativedelta(days=1)  # last day of start month
        cycle_end = derived_end

    # Compute deadline date
    deadline_date = cycle_end - relativedelta(days=days_before_end)
    # Set to end of day to avoid off-by-one display
    deadline = deadline_date.replace(hour=23, minute=59, second=59, microsecond=0)
    return deadline


def get_forecast_months(cycle_start: datetime) -> List[Dict[str, Any]]:
    """
    Get only the forecast months (future months) from a cycle
    Excludes historical months
    """
    period = calculate_16_month_period(cycle_start)

    # Filter only future months
    forecast_months = [
        month for month in period["months"]
        if month["isFuture"] or month["isCurrent"]
    ]

    return forecast_months


def get_historical_months(cycle_start: datetime) -> List[Dict[str, Any]]:
    """
    Get only the historical months from a cycle
    """
    period = calculate_16_month_period(cycle_start)

    # Filter only historical months
    historical_months = [
        month for month in period["months"]
        if month["isHistorical"]
    ]

    return historical_months
