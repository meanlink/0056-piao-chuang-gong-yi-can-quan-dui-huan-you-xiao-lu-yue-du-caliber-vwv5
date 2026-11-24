from voucher_dates import intersect, month_end

def summarize(cx,month):
    ceiling = month_end(month)
    by_counter = {r["code"]:{"site":r["name"],"voucher_days":0,"redemptions":0}
                  for r in cx.execute("SELECT * FROM meal_counters ORDER BY code")}
    vouchers = cx.execute("""
      SELECT v.issued_on,v.expires_on,b.counter FROM meal_vouchers v JOIN meal_batches b ON v.batch=b.code
      WHERE v.issued_on <= %s AND v.expires_on >= %s
    """,(ceiling,month))
    for voucher in vouchers:
        by_counter[voucher["counter"]]["voucher_days"] += intersect(voucher["issued_on"],voucher["expires_on"],month)
    redeemed = cx.execute("""
      SELECT r.counter,count(*) AS total FROM meal_redemptions r LEFT JOIN meal_reversals a ON r.id=a.redemption_id
      WHERE r.used_on BETWEEN %s AND %s AND a.redemption_id IS NULL GROUP BY r.counter
    """,(month,ceiling))
    for row in redeemed:
        by_counter[row["counter"]]["redemptions"] = row["total"]
    rows = list(by_counter.values())
    total = {"site":"合计","voucher_days":sum(r["voucher_days"] for r in rows),
             "redemptions":sum(r["redemptions"] for r in rows)}
    for row in [*rows,total]:
        days=row["voucher_days"]
        row["per_hundred_days"] = round(100*row["redemptions"]/days,2) if days else None
    return {"month":month.isoformat(),"rows":rows,"total":total}
