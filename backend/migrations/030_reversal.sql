CREATE TABLE IF NOT EXISTS meal_reversals (
 redemption_id bigint PRIMARY KEY REFERENCES meal_redemptions(id),
 reason text NOT NULL CHECK(length(reason)>=4),
 approved_by text NOT NULL
);
