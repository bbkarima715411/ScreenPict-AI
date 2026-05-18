import re


def classify_number(number: str, source: str) -> dict[str, str | int]:
    cleaned_number = re.sub(r"\D", "", number)
    length = len(cleaned_number)

    if length == 10 and cleaned_number.startswith(("06", "07")):
        return {
            "numero": cleaned_number,
            "type": "Téléphone mobile",
            "confiance": 94,
            "methode": f"{source} + règle IA : préfixe mobile FR + longueur",
        }

    if length == 10 and cleaned_number.startswith(("01", "02", "03", "04", "05", "09")):
        return {
            "numero": cleaned_number,
            "type": "Téléphone fixe",
            "confiance": 90,
            "methode": f"{source} + règle IA : préfixe fixe FR + longueur",
        }

    if length == 13:
        return {
            "numero": cleaned_number,
            "type": "Code EAN-13 / code-barres possible",
            "confiance": 96 if source == "Code-barres" else 88,
            "methode": f"{source} + règle IA : longueur standard EAN-13",
        }

    if length == 8:
        return {
            "numero": cleaned_number,
            "type": "Code EAN-8 / code court possible",
            "confiance": 94 if source == "Code-barres" else 82,
            "methode": f"{source} + règle IA : longueur standard EAN-8",
        }

    if 11 <= length <= 18:
        return {
            "numero": cleaned_number,
            "type": "Référence fournisseur ou suivi",
            "confiance": 86 if source == "Code-barres" else 72,
            "methode": f"{source} + règle IA : identifiant long",
        }

    if 5 <= length <= 10:
        return {
            "numero": cleaned_number,
            "type": "Référence interne possible",
            "confiance": 78 if source == "Code-barres" else 64,
            "methode": f"{source} + règle IA : longueur moyenne",
        }

    return {
        "numero": cleaned_number,
        "type": "Inconnu",
        "confiance": 45,
        "methode": f"{source} + règle IA : motif non reconnu",
    }


def analyze_numbers(ocr_numbers: list[str], barcode_numbers: list[str]) -> list[dict[str, str | int]]:
    results = []
    seen_numbers = set()

    for number in barcode_numbers:
        result = classify_number(number, "Code-barres")
        results.append(result)
        seen_numbers.add(result["numero"])

    for number in ocr_numbers:
        result = classify_number(number, "OCR")
        if result["numero"] not in seen_numbers:
            results.append(result)
            seen_numbers.add(result["numero"])

    return results
