from functools import lru_cache

from services.config import MODEL_PATH
LABELS = {
    "telephone_belge": "Téléphone belge",
    "telephone_international": "Téléphone international",
    "code_barres_ean13": "Code-barres EAN-13",
    "reference_produit": "Référence produit",
    "email": "Email",
    "date": "Date",
}


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        return None

    try:
        import joblib
    except ImportError:
        return None

    return joblib.load(MODEL_PATH)


def predict_text_type(text: str) -> dict[str, str | int] | None:
    model = load_model()

    if model is None or not text.strip():
        return None

    predicted_label = model.predict([text])[0]
    confidence = 70

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]
        confidence = int(max(probabilities) * 100)

    return {
        "label": predicted_label,
        "type": LABELS.get(predicted_label, predicted_label),
        "confiance": confidence,
        "methode": "Classification ML scikit-learn",
    }
