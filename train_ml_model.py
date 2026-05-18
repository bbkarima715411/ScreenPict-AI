import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

from services.config import MODEL_DIR, MODEL_PATH, TRAINING_DATASET_PATH


def train_model() -> None:
    dataset = pd.read_csv(TRAINING_DATASET_PATH)
    x_train, x_test, y_train, y_test = train_test_split(
        dataset["text"],
        dataset["label"],
        test_size=0.25,
        random_state=42,
        stratify=dataset["label"],
    )

    model = Pipeline([
        ("vectorizer", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    print(classification_report(y_test, predictions, zero_division=0))

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Modèle sauvegardé : {MODEL_PATH}")


if __name__ == "__main__":
    train_model()
