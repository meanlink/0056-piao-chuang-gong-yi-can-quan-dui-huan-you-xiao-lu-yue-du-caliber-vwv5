from datetime import date
from month_close import archive

def run(cx,kind,data):
    if kind!="archive_voucher_month":
        raise ValueError(kind)
    return archive(cx,date.fromisoformat(data["month"]))
