"""
extract.py

Task 3.1 - Extract
Lee el archivo fuente (data/raw/candidates.csv) y lo carga en un DataFrame de Pandas.
No se realiza ninguna transformación de negocio en este paso; el archivo original
se conserva sin modificar en data/raw/.
"""

import os
import pandas as pd

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "candidates.csv")


def extract(path: str = RAW_PATH) -> pd.DataFrame:
    """
    Lee el CSV fuente separado por ';' y retorna un DataFrame sin transformar.

    Parameters
    ----------
    path : str
        Ruta al archivo CSV fuente.

    Returns
    -------
    pd.DataFrame
        Datos crudos, tal como llegan del origen.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo fuente en: {path}")

    df = pd.read_csv(path, sep=";")
    return df


if __name__ == "__main__":
    data = extract()
    print(f"Extract OK: {data.shape[0]} filas, {data.shape[1]} columnas")
    print(data.dtypes)
