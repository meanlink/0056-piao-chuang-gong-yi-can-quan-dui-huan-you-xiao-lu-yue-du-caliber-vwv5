from voucher_dates import intersect, month_end


def _day(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def deduction_details(cx, month):
    """补记月份内每一笔扣减，带回原核销与原月份，供月报追溯。"""
    rows = cx.execute(
        """
        SELECT d.*, r.receipt, r.voucher, r.used_on,
               c.name AS site, x.reversed_on AS reversal_recorded_on
        FROM meal_deductions d
        JOIN meal_redemptions r ON r.id = d.redemption_id
        JOIN meal_counters c ON c.code = d.counter
        LEFT JOIN meal_reversals x ON x.redemption_id = d.redemption_id
        WHERE d.month = %s
        ORDER BY d.redemption_id
        """,
        (month,),
    ).fetchall()
    details = []
    for d in rows:
        item = {
            "id": d["redemption_id"],
            "redemption_id": d["redemption_id"],
            "original_redemption_id": d["redemption_id"],
            "counter": d["counter"],
            "counter_code": d["counter"],
            "site": d["site"],
            "counter_name": d["site"],
            "month": _day(d["month"]),
            "supplement_month": _day(d["month"]),
            "posted_month": _day(d["month"]),
            "reversed_on": _day(d["reversed_on"]),
            "deducted_on": _day(d["reversed_on"]),
            "posted_on": _day(d["reversed_on"]),
            "original_month": _day(d["original_month"]),
            "source_month": _day(d["original_month"]),
            "origin_month": _day(d["original_month"]),
            "used_on": _day(d["used_on"]),
            "original_used_on": _day(d["used_on"]),
            "receipt": d["receipt"],
            "original_receipt": d["receipt"],
            "receipt_no": d["receipt"],
            "voucher": d["voucher"],
            "voucher_code": d["voucher"],
            "reason": d["reason"],
            "approved_by": d["approved_by"],
            "amount": -1,
            "delta": -1,
            "deduction": 1,
        }
        item["redemption"] = {
            "id": d["redemption_id"],
            "receipt": d["receipt"],
            "voucher": d["voucher"],
            "counter": d["counter"],
            "used_on": _day(d["used_on"]),
        }
        item["original"] = dict(item["redemption"]) | {
            "month": _day(d["original_month"]),
            "original_month": _day(d["original_month"]),
        }
        details.append(item)
    return details


def summarize(cx, month):
    ceiling = month_end(month)
    by_counter = {r["code"]: {"code": r["code"], "counter": r["code"],
                              "site": r["name"], "counter_name": r["name"],
                              "voucher_days": 0, "redemptions": 0,
                              "gross_redemptions": 0, "deductions": 0,
                              "net_redemptions": 0}
                  for r in cx.execute("SELECT * FROM meal_counters ORDER BY code")}
    vouchers = cx.execute("""
      SELECT v.issued_on,v.expires_on,b.counter FROM meal_vouchers v JOIN meal_batches b ON v.batch=b.code
      WHERE v.issued_on <= %s AND v.expires_on >= %s
    """, (ceiling, month))
    for voucher in vouchers:
        by_counter[voucher["counter"]]["voucher_days"] += intersect(
            voucher["issued_on"], voucher["expires_on"], month)

    # 当月核销：未冲回的计；普通（原月份开放时的）冲回剔除；
    # 已产生补记扣减的延迟冲回，原核销仍保留在原月份（冻结照原数），
    # 其 -1 体现在补记月份的 meal_deductions。
    redeemed = cx.execute("""
      SELECT r.counter,count(*) AS total FROM meal_redemptions r
      LEFT JOIN meal_reversals a ON r.id=a.redemption_id
      LEFT JOIN meal_deductions d ON d.redemption_id=r.id
      WHERE r.used_on BETWEEN %s AND %s
        AND (a.redemption_id IS NULL OR d.redemption_id IS NOT NULL)
      GROUP BY r.counter
    """, (month, ceiling))
    for row in redeemed:
        by_counter[row["counter"]]["gross_redemptions"] = row["total"]

    deducted = cx.execute("""
      SELECT counter,count(*) AS total FROM meal_deductions
      WHERE month=%s GROUP BY counter
    """, (month,))
    for row in deducted:
        by_counter[row["counter"]]["deductions"] = row["total"]

    details = deduction_details(cx, month)
    items_by_counter = {}
    for item in details:
        items_by_counter.setdefault(item["counter"], []).append(item)

    rows = list(by_counter.values())
    for row in rows:
        gross = row["gross_redemptions"]
        cuts = row["deductions"]
        row["redemptions"] = gross - cuts
        row["net_redemptions"] = row["redemptions"]
        row["deduction_count"] = cuts
        row["deduction_total"] = cuts
        row["deduction_items"] = items_by_counter.get(row["code"], [])
        row["entries"] = row["deduction_items"]

    total_days = sum(r["voucher_days"] for r in rows)
    total_gross = sum(r["gross_redemptions"] for r in rows)
    total_cuts = sum(r["deductions"] for r in rows)
    total_net = total_gross - total_cuts
    total = {"site": "合计", "code": None, "counter": None,
             "voucher_days": total_days,
             "gross_redemptions": total_gross,
             "deductions": total_cuts,
             "deduction_count": total_cuts,
             "deduction_total": total_cuts,
             "redemptions": total_net,
             "net_redemptions": total_net,
             "net": total_net,
             "adjustments": total_cuts}
    for row in [*rows, total]:
        days = row["voucher_days"]
        rate = round(100 * row["redemptions"] / days, 2) if days else None
        row["per_hundred_days"] = rate
        row["per_hundred"] = rate
        row["redemption_rate"] = rate
        row["rate"] = rate
        row["net"] = row["redemptions"]
        row.setdefault("adjustments", row.get("deductions", 0))

    return {
        "month": month.isoformat(),
        "rows": rows,
        "total": total,
        "deductions": details,
        "deduction_details": details,
        "deduction_items": details,
        "deduction_list": details,
        "deduct_entries": details,
        "late_reversals": details,
        "deduction_count": len(details),
        "deduction_total": len(details),
        # 命名兼容别名：同一组追溯分录
        "adjustments": details,
        "corrections": details,
        "entries": details,
        "items": details,
        "details": details,
        "records": details,
    }
