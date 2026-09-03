-- export_results.sql
-- Runs each analytical query (R1-R5) and saves its output as a CSV file
-- inside the results/ folder. Uses the exact same query logic as
-- sql/analytical_queries.sql — this file only adds the \copy export step.
--
-- IMPORTANT: \copy paths are resolved on the CLIENT machine (your computer),
-- relative to the folder you are in when you run psql. Run this from your
-- project's root folder (the one that contains src/, sql/, results/, etc.),
-- and make sure the results/ folder already exists before running this.

-- R1 - Hiring Trends
\copy (SELECT d.year, d.month, d.month_name, COUNT(*) AS total_applications, SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) AS total_hired, ROUND(100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2) AS hire_rate_pct FROM FactApplication f JOIN DimDate d ON f.date_key = d.date_key GROUP BY d.year, d.month, d.month_name ORDER BY d.year, d.month) TO 'results/r1_hiring_trend.csv' WITH CSV HEADER;

-- R2 - Technology Analysis
\copy (SELECT t.technology_name, COUNT(*) AS total_applications, SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) AS total_hired, ROUND(100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2) AS hire_rate_pct FROM FactApplication f JOIN DimTechnology t ON f.technology_key = t.technology_key GROUP BY t.technology_name ORDER BY total_hired DESC) TO 'results/r2_technology_analysis.csv' WITH CSV HEADER;

-- R3 - Candidate Profile Analysis
\copy (SELECT s.seniority_name, ROUND(AVG(f.yoe), 1) AS avg_yoe, COUNT(*) AS total_applications, SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) AS total_hired, ROUND(100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2) AS hire_rate_pct FROM FactApplication f JOIN DimSeniority s ON f.seniority_key = s.seniority_key GROUP BY s.seniority_name ORDER BY hire_rate_pct DESC) TO 'results/r3_candidate_profile.csv' WITH CSV HEADER;

-- R4 - Experience vs. Hiring Outcome
\copy (SELECT s.seniority_name, CASE WHEN f.yoe <= 5 THEN '0-5 years' WHEN f.yoe <= 15 THEN '6-15 years' ELSE '16+ years' END AS yoe_range, COUNT(*) AS total_applications, SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) AS total_hired, ROUND(100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2) AS hire_rate_pct FROM FactApplication f JOIN DimSeniority s ON f.seniority_key = s.seniority_key GROUP BY s.seniority_name, yoe_range ORDER BY s.seniority_name, yoe_range) TO 'results/r4_experience_vs_outcome.csv' WITH CSV HEADER;

-- R5 - Geographic Recruitment Analysis
\copy (SELECT c.country_name, COUNT(*) AS total_applications, SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) AS total_hired, ROUND(100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2) AS hire_rate_pct FROM FactApplication f JOIN DimCountry c ON f.country_key = c.country_key GROUP BY c.country_name HAVING COUNT(*) >= 50 ORDER BY total_applications DESC LIMIT 20) TO 'results/r5_geographic_analysis.csv' WITH CSV HEADER;
