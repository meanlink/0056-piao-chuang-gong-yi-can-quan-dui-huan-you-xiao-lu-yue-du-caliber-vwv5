from fastapi import HTTPException
from psycopg.types.json import Jsonb
from core import enqueue
from exposure import summarize
from month_guard import lock_ledger, verify_open

def preview(cx,month):
    if month.day != 1:
        raise HTTPException(422,"取对应月份第 1 天")
    row = cx.execute("SELECT * FROM meal_months WHERE month=%s",(month,)).fetchone()
    status = row["status"] if row else "open"
    report = row["result"] if row and row["result"] is not None else summarize(cx,month)
    # 同时提供 {status,report} 包装与顶层平铺字段，兼容两种读取方式。
    return {**report, "status": status, "report": report}

def submit(cx,month,signer):
    if month.day != 1:
        raise HTTPException(422,"取对应月份第 1 天")
    lock_ledger(cx)
    verify_open(cx,month)
    # 零券日通常仍不可封账；但若该月已有待封存的补记扣减，
    # 则允许封账，summarize 在零分母时把 per_hundred_days 留空（null）。
    preview_report = summarize(cx,month)
    if preview_report["total"]["voucher_days"] == 0 and preview_report.get("deduction_count",0) == 0:
        raise HTTPException(409,"这个月没有可计量券日")
    job_id=enqueue(cx,"archive_voucher_month",{"month":month.isoformat()})
    cx.execute("INSERT INTO meal_months(month,status,approved_by,job_id) VALUES (%s,'queued',%s,%s)",(month,signer,job_id))
    return {"job_id":job_id}

def archive(cx,month):
    lock_ledger(cx)
    report=summarize(cx,month)
    cx.execute("UPDATE meal_months SET status='closed',result=%s WHERE month=%s",(Jsonb(report),month))
    return report
