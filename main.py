from flask import Flask, render_template, request, redirect

import json
import os

app = Flask(__name__)

# Charger les traductions
def load_tr(lang):
    path = os.path.join("translations", f"{lang}.json")
    if not os.path.exists(path):
        lang = "fr"
        path = "translations/fr.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home_redirect():
    return redirect("/fr/accueil")

@app.route("/<lang>/accueil")
def accueil(lang):
    tr = load_tr(lang)
    return render_template("accueil.html", tr=tr, lang=lang)

@app.route("/<lang>/legendes")
def legendes(lang):
    tr = load_tr(lang)
    return render_template("legendes.html", tr=tr, lang=lang)

@app.route("/<lang>/apropos")
def apropos(lang):
    tr = load_tr(lang)
    return render_template("apropos.html", tr=tr, lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
