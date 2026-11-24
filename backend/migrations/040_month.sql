CREATE TABLE IF NOT EXISTS meal_months (
 month date PRIMARY KEY CHECK(extract(day FROM month)=1),
 status text NOT NULL CHECK(status IN ('queued','closed')),
 approved_by text NOT NULL,
 job_id bigint REFERENCES app_jobs(id),
 result jsonb,
 CHECK((status='closed')=(result IS NOT NULL))
);
