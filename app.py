from datetime import datetime
from pathlib import Path

import pytesseract
from flask import Flask, flash, redirect, render_template, request, send_file, send_from_directory, url_for
from PIL import Image
from werkzeug.utils import secure_filename

from services.barcode_service import extract_barcode_numbers
from services.classification_service import analyze_numbers, classify_number
from services.config import ALLOWED_EXTENSIONS, UPLOAD_DIR
from services.export_service import export_saved_numbers_to_excel
from services.ocr_service import configure_tesseract, extract_ocr_text_items
from services.storage_service import delete_saved_number, ensure_directories, read_saved_numbers, save_results

app = Flask(__name__)
app.secret_key = "local-only-secret-key"


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    ensure_directories()
    analysis_results = []
    uploaded_filename = None
    preview_url = None

    if request.method == "POST":
        if request.form.get("action") == "confirm":
            confirmed_number = request.form.get("confirmed_number", "").strip()
            uploaded_filename = request.form.get("uploaded_filename", "").strip()

            if not confirmed_number:
                flash("Veuillez saisir ou confirmer un numéro avant l'enregistrement.", "error")
                return redirect(url_for("index"))

            analysis_results = [classify_number(confirmed_number, "Validation humaine")]
            save_results(uploaded_filename or "saisie-manuelle", analysis_results)
            flash("Numéro validé et enregistré.", "success")
            return redirect(url_for("index"))

        uploaded_file = request.files.get("photo")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Veuillez sélectionner une photo.", "error")
            return redirect(url_for("index"))

        if not is_allowed_file(uploaded_file.filename):
            flash("Format non accepté. Utilisez PNG, JPG, JPEG, BMP, TIFF ou WEBP.", "error")
            return redirect(url_for("index"))

        original_filename = secure_filename(Path(uploaded_file.filename).name)
        uploaded_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{original_filename}"
        image_path = UPLOAD_DIR / uploaded_filename
        uploaded_file.save(image_path)
        preview_url = url_for("uploaded_file", filename=uploaded_filename)

        try:
            image = Image.open(image_path)
            ocr_items = extract_ocr_text_items(image)
            barcode_numbers = extract_barcode_numbers(image_path)
            analysis_results = analyze_numbers(ocr_items, barcode_numbers)
        except pytesseract.TesseractNotFoundError:
            flash("Tesseract OCR n'est pas installé ou n'est pas accessible dans le PATH Windows.", "error")
        except Exception as error:
            flash(f"Impossible d'analyser cette image : {error}", "error")

        if analysis_results:
            flash(f"{len(analysis_results)} résultat(s) proposé(s). Vérifiez avant d'enregistrer.", "success")
        else:
            flash("Aucun chiffre reconnu automatiquement. Vous pouvez saisir le numéro manuellement depuis l'image.", "warning")

    saved_numbers = [
        {**row, "row_index": index}
        for index, row in reversed(list(enumerate(read_saved_numbers())))
    ]
    return render_template(
        "index.html",
        analysis_results=analysis_results,
        uploaded_filename=uploaded_filename,
        preview_url=preview_url,
        saved_numbers=saved_numbers,
    )


@app.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/delete/<int:row_index>", methods=["POST"])
def delete_number(row_index: int):
    if delete_saved_number(row_index):
        flash("Numéro supprimé de la liste.", "success")
    else:
        flash("Impossible de supprimer ce numéro.", "error")

    return redirect(url_for("index"))


@app.route("/export")
def export_csv():
    ensure_directories()
    excel_path = export_saved_numbers_to_excel()
    return send_file(excel_path, as_attachment=True, download_name=excel_path.name)


configure_tesseract()


if __name__ == "__main__":
    ensure_directories()
    app.run(host="127.0.0.1", port=5000, debug=False)
