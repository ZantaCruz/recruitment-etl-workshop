-- analytical_queries.sql
-- Task 6: Analytical Queries and KPIs
-- Todas las consultas se ejecutan directamente contra el Data Warehouse
-- (DimDate, DimTechnology, DimSeniority, DimCountry, FactApplication).

-- ============================================================
-- R1 - Hiring Trends
-- Pregunta: ¿Cómo evoluciona la tasa de contratación mes a mes?
-- ============================================================
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*)                                            AS total_applications,
    SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END)         AS total_hired,
    ROUND(
        100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS hire_rate_pct
FROM FactApplication f
JOIN DimDate d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- ============================================================
-- R2 - Technology Analysis
-- Pregunta: ¿Qué tecnologías generan el mayor número y proporción
-- de candidatos contratados?
-- ============================================================
SELECT
    t.technology_name,
    COUNT(*)                                            AS total_applications,
    SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END)         AS total_hired,
    ROUND(
        100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS hire_rate_pct
FROM FactApplication f
JOIN DimTechnology t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY total_hired DESC;


-- ============================================================
-- R3 - Candidate Profile Analysis
-- Pregunta: ¿Cómo varían los resultados de contratación según
-- seniority y años de experiencia?
-- ============================================================
SELECT
    s.seniority_name,
    ROUND(AVG(f.yoe), 1)                                AS avg_yoe,
    COUNT(*)                                            AS total_applications,
    SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END)         AS total_hired,
    ROUND(
        100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS hire_rate_pct
FROM FactApplication f
JOIN DimSeniority s ON f.seniority_key = s.seniority_key
GROUP BY s.seniority_name
ORDER BY hire_rate_pct DESC;


-- ============================================================
-- R4 - Experience vs. Hiring Outcome
-- Pregunta: dentro de cada nivel de seniority, ¿los candidatos con
-- más años de experiencia tienen mejores resultados?
-- ============================================================
SELECT
    s.seniority_name,
    CASE
        WHEN f.yoe <= 5  THEN '0-5 años'
        WHEN f.yoe <= 15 THEN '6-15 años'
        ELSE '16+ años'
    END                                                  AS yoe_range,
    COUNT(*)                                            AS total_applications,
    SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END)         AS total_hired,
    ROUND(
        100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS hire_rate_pct
FROM FactApplication f
JOIN DimSeniority s ON f.seniority_key = s.seniority_key
GROUP BY s.seniority_name, yoe_range
ORDER BY s.seniority_name, yoe_range;


-- ============================================================
-- R5 - Geographic Recruitment Analysis
-- Pregunta: ¿Qué países generan más aplicaciones y cuáles tienen
-- la mejor tasa de contratación?
-- ============================================================
SELECT
    c.country_name,
    COUNT(*)                                            AS total_applications,
    SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END)         AS total_hired,
    ROUND(
        100.0 * SUM(CASE WHEN f.is_hired THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                    AS hire_rate_pct
FROM FactApplication f
JOIN DimCountry c ON f.country_key = c.country_key
GROUP BY c.country_name
HAVING COUNT(*) >= 50   -- filtra países con volumen estadísticamente relevante
ORDER BY total_applications DESC
LIMIT 20;
