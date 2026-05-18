import csv
from datetime import datetime

from services.config import CSV_COLUMNS, CSV_PATH, DATA_DIR, UPLOAD_DIR


def ensure_directories() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    UPLOAD_DIR.mkdir(exist_ok=True)
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(CSV_COLUMNS)
    else:
        migrate_csv_columns()


def migrate_csv_columns() -> None:
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        rows = list(reader)

    if reader.fieldnames == CSV_COLUMNS:
        return

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "date": row.get("date", ""),
                "fichier": row.get("fichier", ""),
                "numero": row.get("numero", ""),
                "type": row.get("type", "Ancien résultat"),
                "confiance": row.get("confiance", ""),
                "methode": row.get("methode", ""),
            })


def save_results(filename: str, results: list[dict[str, str | int]]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with CSV_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        for result in results:
            writer.writerow([
                now,
                filename,
                result["numero"],
                result["type"],
                result["confiance"],
                result["methode"],
            ])


def read_saved_numbers() -> list[dict[str, str]]:
    ensure_directories()
    with CSV_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        return list(reader)


def delete_saved_number(row_index: int) -> bool:
    rows = read_saved_numbers()

    if row_index < 0 or row_index >= len(rows):
        return False

    del rows[row_index]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    return True
