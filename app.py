from flask import Flask, render_template, send_from_directory, abort, redirect
import json
import os

app = Flask(__name__)

# Chargement des traductions
TRANSLATION_FILE = "translations.json"

if not os.path.exists(TRANSLATION_FILE):
    raise FileNotFoundError("Le fichier translations.json est introuvable à la racine du projet.")

with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
    translations = json.load(f)

def t(lang, key):
    if lang not in translations:
        lang = "fr"
    return translations[lang].get(key, key)

# ------------------------------------------------
# NOUVELLE ROUTE QUI FIXE TON ERREUR :
# ------------------------------------------------
@app.route("/")
def root_redirect():
    return redirect("/fr/accueil")

# Accueil
@app.route("/<lang>/accueil")
def accueil(lang):
    return render_template("home.html", t=lambda k: t(lang, k), lang=lang)

# Légendes
@app.route("/<lang>/legendes")
def legendes(lang):
    return render_template("legendes.html", t=lambda k: t(lang, k), lang=lang)

# Admin
@app.route("/admin/<lang>")
def admin(lang):
    return render_template("admin.html", t=lambda k: t(lang, k), lang=lang)

# Fichiers statiques
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
