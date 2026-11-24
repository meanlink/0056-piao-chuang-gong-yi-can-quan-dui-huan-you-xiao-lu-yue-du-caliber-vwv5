from datetime import date, datetime, timedelta

def month_start(day):
    return day.replace(day=1)

def parse_month(value):
    """Accept YYYY-MM-DD, YYYY-MM or a date/datetime and return the 1st."""
    if isinstance(value, datetime):
        return value.date().replace(day=1)
    if isinstance(value, date):
        return value.replace(day=1)
    text = str(value).strip()
    if len(text) == 7 and text[4] == "-":
        return date.fromisoformat(text + "-01")
    return date.fromisoformat(text[:10]).replace(day=1)

def month_end(month):
    return (month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

def intersect(first, last, month):
    left, right = max(first, month), min(last, month_end(month))
    return max(0, (right-left).days+1)

def each_month(first,last):
    month = month_start(first)
    while month <= last:
        yield month
        month = month_end(month)+timedelta(days=1)
