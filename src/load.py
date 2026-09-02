"""
load.py

Task 5 - Load the Data Warehouse

Crea el esquema en PostgreSQL (sql/create_tables.sql) y carga las tablas
en el orden correcto respetando las llaves foráneas:

    DimDate -> DimTechnology -> DimSeniority -> DimCountry -> FactApplication

La conexión se configura mediante variables de entorno (ver .env.example):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def get_engine():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "recruitment_dw")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url)


def create_schema(engine):
    """Ejecuta sql/create_tables.sql para crear el esquema en estrella."""
    ddl_path = SQL_DIR / "create_tables.sql"
    ddl = ddl_path.read_text()

    with engine.begin() as conn:
        for statement in ddl.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))

    print("Esquema creado correctamente.")


def load_dimensions(engine, model: dict):
    """Carga las dimensiones antes que la tabla de hechos."""
    model["dim_date"].to_sql("dimdate", engine, if_exists="append", index=False)
    print(f"DimDate cargada: {len(model['dim_date'])} filas")

    model["dim_technology"].to_sql("dimtechnology", engine, if_exists="append", index=False)
    print(f"DimTechnology cargada: {len(model['dim_technology'])} filas")

    model["dim_seniority"].to_sql("dimseniority", engine, if_exists="append", index=False)
    print(f"DimSeniority cargada: {len(model['dim_seniority'])} filas")

    model["dim_country"].to_sql("dimcountry", engine, if_exists="append", index=False)
    print(f"DimCountry cargada: {len(model['dim_country'])} filas")


def load_fact(engine, model: dict):
    """Carga la tabla de hechos, última en el orden de carga."""
    model["fact_application"].to_sql(
        "factapplication", engine, if_exists="append", index=False, chunksize=5000
    )
    print(f"FactApplication cargada: {len(model['fact_application'])} filas")


def validate_load(engine):
    """
    Task 5 - Validaciones requeridas:
    número de registros cargados y ausencia de referencias de dimensión inválidas.
    """
    with engine.connect() as conn:
        counts = {}
        for table in ["dimdate", "dimtechnology", "dimseniority", "dimcountry", "factapplication"]:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            counts[table] = result

        orphan_check = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM FactApplication f
                LEFT JOIN DimDate d ON f.date_key = d.date_key
                LEFT JOIN DimTechnology t ON f.technology_key = t.technology_key
                LEFT JOIN DimSeniority s ON f.seniority_key = s.seniority_key
                LEFT JOIN DimCountry c ON f.country_key = c.country_key
                WHERE d.date_key IS NULL
                   OR t.technology_key IS NULL
                   OR s.seniority_key IS NULL
                   OR c.country_key IS NULL
                """
            )
        ).scalar()

    print("Validación de carga:")
    for table, count in counts.items():
        print(f"  {table}: {count} registros")
    print(f"  Referencias de dimensión inválidas en FactApplication: {orphan_check}")

    return counts, orphan_check


def load_all(model: dict):
    engine = get_engine()
    create_schema(engine)
    load_dimensions(engine, model)
    load_fact(engine, model)
    validate_load(engine)
    return engine


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    from dimensional_model import build_dimensional_model

    raw = extract()
    prepared = transform(raw)
    dim_model = build_dimensional_model(prepared)
    load_all(dim_model)
