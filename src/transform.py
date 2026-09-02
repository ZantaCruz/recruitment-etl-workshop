"""
transform.py

Task 3.2 - Data Preparation
Task 3.3 - Business Transformation

Decisiones de preparación documentadas:
- No se eliminan filas con Email duplicado: cada fila representa una aplicación
  individual (grano del hecho), no un candidato único. Un mismo candidato puede
  aplicar más de una vez en fechas distintas.
- Application Date se convierte a tipo datetime.
- Se eliminan espacios en blanco sobrantes en columnas de texto.
- No se identificaron valores nulos en el perfilado inicial (Task 1), por lo que
  no se requiere imputación.
- No se identificaron filas duplicadas exactas (todas las columnas).

Regla de negocio (Business Rule - HIRED):
    HIRED = (Code Challenge Score >= 7) AND (Technical Interview Score >= 7)
"""

import pandas as pd

TEXT_COLUMNS = ["First Name", "Last Name", "Email", "Country", "Seniority", "Technology"]


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica la preparación de datos requerida antes de la transformación
    dimensional: tipos de datos, formatos y limpieza básica de texto.
    No aplica reglas de negocio.
    """
    data = df.copy()

    for col in TEXT_COLUMNS:
        data[col] = data[col].astype(str).str.strip()

    data["Application Date"] = pd.to_datetime(data["Application Date"])

    data["YOE"] = data["YOE"].astype(int)
    data["Code Challenge Score"] = data["Code Challenge Score"].astype(int)
    data["Technical Interview Score"] = data["Technical Interview Score"].astype(int)

    return data


def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Implementa la regla de negocio HIRED y agrega columnas derivadas
    necesarias para los requisitos de negocio R1-R5.
    """
    data = df.copy()

    data["is_hired"] = (
        (data["Code Challenge Score"] >= 7) & (data["Technical Interview Score"] >= 7)
    )

    # Atributos derivados de fecha, requeridos por DimDate (R1)
    data["application_year"] = data["Application Date"].dt.year
    data["application_month"] = data["Application Date"].dt.month
    data["application_quarter"] = data["Application Date"].dt.quarter

    return data


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Orquesta la preparación y la transformación de negocio."""
    prepared = prepare(df)
    transformed = apply_business_rules(prepared)
    return transformed


if __name__ == "__main__":
    from extract import extract

    raw = extract()
    result = transform(raw)
    print(f"Transform OK: {result.shape[0]} filas")
    print(f"Candidatos HIRED: {result['is_hired'].sum()} ({result['is_hired'].mean():.2%})")
