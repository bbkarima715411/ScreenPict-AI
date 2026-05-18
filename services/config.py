from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CSV_PATH = DATA_DIR / "numeros_extraits.csv"
EXCEL_PATH = DATA_DIR / "numeros_extraits.xlsx"
TRAINING_DATASET_PATH = DATA_DIR / "training_dataset.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "text_classifier.joblib"
CSV_COLUMNS = ["date", "fichier", "numero", "type", "confiance", "methode"]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff", "webp"}
TESSERACT_CANDIDATES = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    Path.home() / "AppData" / "Local" / "Programs" / "Tesseract-OCR" / "tesseract.exe",
]
