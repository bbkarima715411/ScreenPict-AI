# ScreenPict AI

Application locale intelligente pour reconnaître des numéros sur une photo, les classer automatiquement et les enregistrer dans une liste CSV.

## Objectif du projet

ScreenPict AI analyse une image uploadée par l'utilisateur afin d'extraire les numéros visibles ou encodés dans un code-barres et de leur attribuer un type probable :

- numéro de téléphone mobile ;
- numéro de téléphone fixe ;
- code EAN-13 ou EAN-8 ;
- référence fournisseur ou suivi ;
- référence interne possible ;
- numéro inconnu.

Chaque résultat reçoit aussi un score de confiance et une méthode d'analyse, ce qui permet de présenter le projet comme une première couche d'IA métier basée sur OCR, traitement d'image et règles intelligentes.

## Confidentialité

Cette application fonctionne uniquement en local sur le poste :

- aucune API externe n'est utilisée ;
- aucun hébergement n'est nécessaire ;
- l'application écoute seulement sur `127.0.0.1` ;
- les images et résultats sont stockés dans le dossier local `data/`.

## Fonctionnement

```text
Photo uploadée
→ prétraitement de l'image avec OpenCV
→ reconnaissance OCR avec Tesseract
→ décodage code-barres avec OpenCV
→ extraction des suites de chiffres
→ classification intelligente des numéros
→ sauvegarde locale en CSV
```

## Prérequis

### 1. Installer Python

Installer Python 3.11 ou plus récent depuis :

https://www.python.org/downloads/

Pendant l'installation, cocher l'option `Add Python to PATH`.

### 2. Installer Tesseract OCR

Installer Tesseract OCR pour Windows depuis :

https://github.com/UB-Mannheim/tesseract/wiki

Après installation, vérifier que Tesseract est accessible dans le `PATH` Windows.

Chemin fréquent :

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Installation de l'application

Dans un terminal PowerShell ouvert dans le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lancement

```powershell
python app.py
```

Puis ouvrir dans le navigateur :

```text
http://127.0.0.1:5000
```

## Utilisation

1. Cliquer sur `Sélectionner une photo`.
2. Choisir une image contenant des chiffres.
3. Cliquer sur `Analyser la photo`.
4. Les numéros reconnus sont classés automatiquement.
5. Le bouton `Exporter le CSV` permet de récupérer le fichier `numeros_extraits.csv`.

## Données locales

Les données sont créées automatiquement dans :

```text
data/
```

Contenu :

- `data/uploads/` : copies locales des photos analysées ;
- `data/numeros_extraits.csv` : liste des numéros extraits avec type détecté, confiance et méthode.

## Évolutions possibles

- Améliorer la lecture QR codes.
- Ajouter une base SQLite pour gérer l'historique des analyses.
- Ajouter une correction manuelle des résultats par l'utilisateur.
- Entraîner un modèle Machine Learning local avec `scikit-learn`.
- Ajouter un dashboard avec statistiques et taux de confiance moyen.

## Limites importantes

La qualité de reconnaissance dépend fortement de :

- la netteté de la photo ;
- le contraste ;
- l'orientation ;
- la taille des chiffres ;
- l'absence de bruit visuel autour des numéros.

Pour de meilleurs résultats, utiliser des photos bien cadrées, droites et lumineuses.
