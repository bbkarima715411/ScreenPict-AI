# Roadmap IA ScreenPict-AI

## Architecture actuelle

```text
app.py
services/
  barcode_service.py
  classification_service.py
  config.py
  export_service.py
  ml_service.py
  ocr_service.py
  storage_service.py
data/
  training_dataset.csv
models/
  text_classifier.joblib
train_ml_model.py
```

## Étape 1 - Classification ML

- Entraîner un modèle scikit-learn depuis `data/training_dataset.csv`.
- Sauvegarder le modèle dans `models/text_classifier.joblib`.
- Utiliser `services/ml_service.py` pour prédire le type d'un texte OCR.
- Garder les règles existantes comme fallback.

Commande :

```powershell
py -m pip install -r requirements.txt
py train_ml_model.py
```

## Étape 2 - SQLite

Objectif : remplacer progressivement le CSV par une base locale.

Structure proposée :

```text
database.py
models/
  analysis.py
services/
  history_service.py
```

Table `analyses` :

```text
id
created_at
filename
raw_text
value
type
confidence
method
source
```

## Étape 3 - Historique des analyses

- Une analyse = une image uploadée.
- Une analyse peut contenir plusieurs résultats détectés.
- Afficher une page historique avec détail image + résultats.

## Étape 4 - Recherche

Ajouter une recherche sur :

- numéro
- email
- référence
- type détecté
- nom de fichier
- date d'analyse

## Étape 5 - Amélioration OCR

Axes possibles :

- sauvegarde du texte OCR brut
- scoring par source OCR/code-barres/ML
- comparaison entre plusieurs variantes OCR
- correction automatique de caractères fréquents

## Étape 6 - QR code

Ajouter un service :

```text
services/qr_service.py
```

Options possibles :

- OpenCV `QRCodeDetector`
- ou `pyzbar` si besoin d'un support plus large

## Objectif final

Transformer ScreenPict-AI en application intelligente capable d'identifier automatiquement les informations importantes présentes sur une image : téléphones, emails, dates, références, codes-barres et QR codes.
