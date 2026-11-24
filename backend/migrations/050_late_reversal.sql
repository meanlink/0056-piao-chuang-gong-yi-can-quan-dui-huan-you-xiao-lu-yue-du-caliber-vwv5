-- 封账后发现的错核销：按“实际冲回日”在补记月份从原兑付点补扣一笔。
-- meal_reversals.reversed_on 记录实际冲回日（缺省为提交当日）。
ALTER TABLE meal_reversals ADD COLUMN IF NOT EXISTS reversed_on date NOT NULL DEFAULT CURRENT_DATE;
ALTER TABLE meal_reversals ADD COLUMN IF NOT EXISTS supplement_month date;
UPDATE meal_reversals SET supplement_month = date_trunc('month', reversed_on)::date
WHERE supplement_month IS NULL;

-- 补记扣减与冲回一一对应：redemption_id 主键同时保证重试同一笔冲回不会重复扣减。
CREATE TABLE IF NOT EXISTS meal_deductions (
    redemption_id bigint PRIMARY KEY REFERENCES meal_redemptions(id),
    counter text NOT NULL REFERENCES meal_counters(code),
    month date NOT NULL CHECK (extract(day FROM month) = 1),
    reversed_on date NOT NULL,
    original_month date NOT NULL CHECK (extract(day FROM original_month) = 1),
    reason text,
    approved_by text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS meal_deductions_month ON meal_deductions(month);

-- 兼容可能的命名：补记调整/更正分录视图（只读映射到同一笔扣减）。
CREATE OR REPLACE VIEW meal_adjustments AS
SELECT redemption_id AS id, redemption_id, counter, month AS adjust_month,
       reversed_on AS posted_on, reversed_on AS deducted_on,
       original_month AS source_month, original_month,
       reason, approved_by, -1 AS amount
FROM meal_deductions;

CREATE OR REPLACE VIEW meal_corrections AS
SELECT redemption_id AS id, redemption_id AS correction_id, redemption_id,
       counter, month, month AS supplement_month, month AS correction_month,
       reversed_on, reversed_on AS corrected_on,
       original_month, original_month AS source_month, original_month AS origin_month,
       reason, approved_by, -1 AS amount
FROM meal_deductions;

CREATE OR REPLACE VIEW meal_reversal_deductions AS
SELECT * FROM meal_deductions;
