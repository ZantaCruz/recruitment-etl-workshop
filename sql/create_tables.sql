-- create_tables.sql
-- Task 5: Load the Data Warehouse
-- Esquema en estrella para el proceso de negocio "Evaluación de aplicaciones
-- de candidatos en procesos de reclutamiento técnico".
-- Motor: PostgreSQL

DROP TABLE IF EXISTS FactApplication;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS DimTechnology;
DROP TABLE IF EXISTS DimSeniority;
DROP TABLE IF EXISTS DimCountry;

-- ============================================================
-- DIMENSIONES
-- ============================================================

CREATE TABLE DimDate (
    date_key    INTEGER PRIMARY KEY,          -- formato YYYYMMDD
    full_date   DATE NOT NULL,
    day         SMALLINT NOT NULL,
    month       SMALLINT NOT NULL,
    month_name  VARCHAR(20) NOT NULL,
    quarter     SMALLINT NOT NULL,
    year        SMALLINT NOT NULL
);

CREATE TABLE DimTechnology (
    technology_key   SERIAL PRIMARY KEY,
    technology_name  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE DimSeniority (
    seniority_key   SERIAL PRIMARY KEY,
    seniority_name  VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE DimCountry (
    country_key   SERIAL PRIMARY KEY,
    country_name  VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================================
-- TABLA DE HECHOS
-- ============================================================
-- Grano: una fila = una aplicación individual de un candidato,
-- evaluada con dos scores, en una fecha, país, tecnología y
-- nivel de seniority determinados.

CREATE TABLE FactApplication (
    application_id              INTEGER PRIMARY KEY,
    date_key                    INTEGER NOT NULL REFERENCES DimDate(date_key),
    technology_key              INTEGER NOT NULL REFERENCES DimTechnology(technology_key),
    seniority_key                INTEGER NOT NULL REFERENCES DimSeniority(seniority_key),
    country_key                 INTEGER NOT NULL REFERENCES DimCountry(country_key),
    candidate_email              VARCHAR(255) NOT NULL,
    yoe                          SMALLINT NOT NULL,
    code_challenge_score         SMALLINT NOT NULL CHECK (code_challenge_score BETWEEN 0 AND 10),
    technical_interview_score    SMALLINT NOT NULL CHECK (technical_interview_score BETWEEN 0 AND 10),
    is_hired                     BOOLEAN NOT NULL
);

CREATE INDEX idx_fact_date ON FactApplication(date_key);
CREATE INDEX idx_fact_technology ON FactApplication(technology_key);
CREATE INDEX idx_fact_seniority ON FactApplication(seniority_key);
CREATE INDEX idx_fact_country ON FactApplication(country_key);
