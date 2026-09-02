"""
main.py

Orquestador del pipeline ETL completo:
    Extract -> Transform -> Dimensional Model -> Load -> Validate

Ejecución:
    python src/main.py
"""

from extract import extract
from transform import transform
from dimensional_model import build_dimensional_model
from load import load_all


def run():
    print("=== 1. EXTRACT ===")
    raw = extract()
    print(f"{raw.shape[0]} filas extraídas de data/raw/candidates.csv\n")

    print("=== 2. TRANSFORM ===")
    prepared = transform(raw)
    hired_pct = prepared["is_hired"].mean()
    print(f"Regla HIRED aplicada. Tasa de contratación global: {hired_pct:.2%}\n")

    print("=== 3. DIMENSIONAL MODEL ===")
    model = build_dimensional_model(prepared)
    for name, table in model.items():
        print(f"  {name}: {table.shape[0]} filas")
    print()

    print("=== 4. LOAD ===")
    load_all(model)

    print("\nPipeline ETL finalizado correctamente.")


if __name__ == "__main__":
    run()
