-- Long-run HungerCount change, suppressing non-comparable series.
WITH pivoted AS (
  SELECT province_code,
         MAX(total_visits) FILTER (WHERE year = 2019) AS visits_2019,
         MAX(total_visits) FILTER (WHERE year = 2025) AS visits_2025,
         BOOL_AND(comparable_to_2019) AS comparable
  FROM hunger_count
  WHERE year IN (2019, 2025)
  GROUP BY province_code
)
SELECT province_code, visits_2019, visits_2025,
       ROUND(100.0 * (visits_2025::numeric / visits_2019 - 1), 1) AS change_pct
FROM pivoted
WHERE comparable
ORDER BY change_pct DESC;

-- Compare the two measures only where their years overlap.
SELECT h.year, h.province_code, h.total_visits, f.people_pct
FROM hunger_count h
JOIN food_insecurity f USING (year, province_code)
ORDER BY h.year, h.province_code;
