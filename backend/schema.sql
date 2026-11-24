CREATE TABLE IF NOT EXISTS meal_counters(code text PRIMARY KEY,name text NOT NULL);
CREATE TABLE IF NOT EXISTS meal_batches(
 code text PRIMARY KEY,
 counter text NOT NULL REFERENCES meal_counters(code),
 sponsor text NOT NULL
);
CREATE TABLE IF NOT EXISTS meal_vouchers(
 code text PRIMARY KEY,
 batch text NOT NULL REFERENCES meal_batches(code),
 issued_on date NOT NULL,
 expires_on date NOT NULL,
 CHECK(expires_on BETWEEN issued_on AND issued_on+180)
);
