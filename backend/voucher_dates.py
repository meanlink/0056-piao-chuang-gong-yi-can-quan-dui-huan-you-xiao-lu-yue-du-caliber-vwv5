from datetime import date, timedelta

def month_start(day):
    return day.replace(day=1)

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
