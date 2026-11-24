def seed(cx):
    cx.execute("INSERT INTO meal_counters VALUES ('QD','桥东餐站'),('CQ','仓前餐站') ON CONFLICT DO NOTHING")
    cx.execute("INSERT INTO meal_batches VALUES ('QD-11','QD','青穗互助会'),('CQ-11','CQ','邻里茶摊联会') ON CONFLICT DO NOTHING")
    for row in (
        ("QD-111","QD-11","2026-11-11","2026-11-20"),
        ("QD-112","QD-11","2026-10-27","2026-11-10"),
        ("CQ-141","CQ-11","2026-11-01","2026-11-30"),
        ("CQ-142","CQ-11","2026-11-26","2026-12-02"),
    ):
        cx.execute("INSERT INTO meal_vouchers VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING",row)
    cx.execute("""INSERT INTO meal_redemptions(voucher,counter,used_on,receipt)
    VALUES ('CQ-141','CQ','2026-11-13','CQ-S013') ON CONFLICT DO NOTHING""")
