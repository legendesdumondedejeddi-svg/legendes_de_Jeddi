from flask import Flask, render_template, request, redirect, url_for, flash
import json, os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "devsecret")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

LANGUAGES = ["fr", "en", "es", "de", "it"]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

translations = load_json("data/translations.json")
legendes_db = load_json("data/legendes.json")

def trans(key, lang):
    if lang not in translations:
        lang = "fr"
    return translations[lang].get(key, key)

def get_legende(slug):
    for lg in legendes_db["legendes"]:
        if lg["slug"] == slug:
            return lg
    return None

@app.route("/")
@app.route("/<lang>")
def accueil(lang="fr"):
    return render_template("accueil.html", lang=lang, trans=lambda k: trans(k, lang))

@app.route("/<lang>/legendes")
def liste_legendes(lang="fr"):
    lst = []
    for lg in legendes_db["legendes"]:
        bloc = lg.get(lang, lg.get("fr"))
        lst.append({
            "slug": lg["slug"],
            "titre": bloc["titre"],
            "image": lg.get("image")
        })
    return render_template("liste_legendes.html", legendes=lst, lang=lang, trans=lambda k: trans(k, lang))

@app.route("/<lang>/legende/<slug>")
def legende(lang="fr", slug=""):
    lg = get_legende(slug)
    if not lg:
        return "Not found", 404

    bloc = lg.get(lang, lg.get("fr"))

    return render_template("legende.html",
                           legende=bloc,
                           image=lg.get("image"),
                           lang=lang,
                           trans=lambda k: trans(k, lang))

@app.route("/<lang>/apropos")
def apropos(lang="fr"):
    return render_template("apropos.html", lang=lang, trans=lambda k: trans(k, lang))

@app.route("/<lang>/grimoire")
def grimoire(lang="fr"):
    return render_template("grimoire.html", lang=lang, trans=lambda k: trans(k, lang))

@app.route("/<lang>/don")
def don(lang="fr"):
    return render_template("don.html", lang=lang, trans=lambda k: trans(k, lang))

@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if request.method == "POST":
        if request.form.get("pwd") == ADMIN_PASSWORD:
            return render_template("admin_dashboard.html")
        flash("Mot de passe incorrect", "error")
    return render_template("admin_dashboard.html", login=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

