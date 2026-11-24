CREATE TABLE IF NOT EXISTS meal_redemptions (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 voucher text NOT NULL REFERENCES meal_vouchers(code),
 counter text NOT NULL REFERENCES meal_counters(code),
 used_on date NOT NULL,
 receipt text NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS meal_redemptions_day ON meal_redemptions(used_on);
