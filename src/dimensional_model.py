"""
dimensional_model.py

Task 4 - Dimensional Transformation

Transforma los datos preparados (transform.py) en las estructuras dimensionales
definidas en el diseño del Star Schema:

    DimDate, DimTechnology, DimSeniority, DimCountry -> FactApplication

Proceso conceptual:
    Prepared Candidate Data -> Dimension Records -> Surrogate Keys ->
    Key Mapping -> Fact Table

Grano de FactApplication: una fila representa una aplicación individual de un
candidato, evaluada con dos scores, en una fecha, país, tecnología y nivel de
seniority determinados.
"""

import pandas as pd


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera DimDate a partir de las fechas únicas de aplicación.
    date_key con formato YYYYMMDD (entero), consistente con el estándar de
    Data Warehousing para dimensiones de fecha.
    """
    dates = df["Application Date"].drop_duplicates().sort_values().reset_index(drop=True)

    dim_date = pd.DataFrame({"full_date": dates})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["day"] = dim_date["full_date"].dt.day

    return dim_date[["date_key", "full_date", "day", "month", "month_name", "quarter", "year"]]


def build_dim_technology(df: pd.DataFrame) -> pd.DataFrame:
    """Genera DimTechnology con surrogate key autoincremental (technology_key)."""
    values = sorted(df["Technology"].drop_duplicates().tolist())
    dim = pd.DataFrame({"technology_name": values})
    dim.insert(0, "technology_key", range(1, len(dim) + 1))
    return dim


def build_dim_seniority(df: pd.DataFrame) -> pd.DataFrame:
    """Genera DimSeniority con surrogate key autoincremental (seniority_key)."""
    values = sorted(df["Seniority"].drop_duplicates().tolist())
    dim = pd.DataFrame({"seniority_name": values})
    dim.insert(0, "seniority_key", range(1, len(dim) + 1))
    return dim


def build_dim_country(df: pd.DataFrame) -> pd.DataFrame:
    """Genera DimCountry con surrogate key autoincremental (country_key)."""
    values = sorted(df["Country"].drop_duplicates().tolist())
    dim = pd.DataFrame({"country_name": values})
    dim.insert(0, "country_key", range(1, len(dim) + 1))
    return dim


def build_fact_application(
    df: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_technology: pd.DataFrame,
    dim_seniority: pd.DataFrame,
    dim_country: pd.DataFrame,
) -> pd.DataFrame:
    """
    Mapea cada aplicación a las surrogate keys correspondientes y construye
    la tabla de hechos FactApplication según el grano declarado.
    """
    data = df.copy()
    data["date_key"] = data["Application Date"].dt.strftime("%Y%m%d").astype(int)

    fact = data.merge(
        dim_technology, left_on="Technology", right_on="technology_name", how="left"
    ).merge(
        dim_seniority, left_on="Seniority", right_on="seniority_name", how="left"
    ).merge(
        dim_country, left_on="Country", right_on="country_name", how="left"
    )

    # Validación de integridad: ningún registro debe quedar sin surrogate key
    missing = fact[
        fact["technology_key"].isna()
        | fact["seniority_key"].isna()
        | fact["country_key"].isna()
    ]
    if not missing.empty:
        raise ValueError(
            f"Se encontraron {len(missing)} registros sin surrogate key asignada."
        )

    fact_application = fact[
        [
            "date_key",
            "technology_key",
            "seniority_key",
            "country_key",
            "Email",
            "YOE",
            "Code Challenge Score",
            "Technical Interview Score",
            "is_hired",
        ]
    ].rename(
        columns={
            "Email": "candidate_email",
            "YOE": "yoe",
            "Code Challenge Score": "code_challenge_score",
            "Technical Interview Score": "technical_interview_score",
        }
    )

    fact_application.insert(0, "application_id", range(1, len(fact_application) + 1))
    fact_application["is_hired"] = fact_application["is_hired"].astype(bool)

    return fact_application


def build_dimensional_model(df: pd.DataFrame) -> dict:
    """
    Construye el conjunto completo de dimensiones y la tabla de hechos
    a partir de los datos ya preparados y transformados (transform.py).
    """
    dim_date = build_dim_date(df)
    dim_technology = build_dim_technology(df)
    dim_seniority = build_dim_seniority(df)
    dim_country = build_dim_country(df)

    fact_application = build_fact_application(
        df, dim_date, dim_technology, dim_seniority, dim_country
    )

    return {
        "dim_date": dim_date,
        "dim_technology": dim_technology,
        "dim_seniority": dim_seniority,
        "dim_country": dim_country,
        "fact_application": fact_application,
    }


if __name__ == "__main__":
    from extract import extract
    from transform import transform

    raw = extract()
    prepared = transform(raw)
    model = build_dimensional_model(prepared)

    for name, table in model.items():
        print(f"{name}: {table.shape[0]} filas, {table.shape[1]} columnas")
