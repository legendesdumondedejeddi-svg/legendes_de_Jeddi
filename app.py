import os
from flask import Flask, render_template, request, abort

app = Flask(__name__)

LANGS = ["fr", "en", "es", "de", "it"]

# -------------------------------
# ROUTES ACCUEIL
# -------------------------------

@app.route("/")
def home_redirect():
    return render_template("accueil_fr.html", lang="fr")

@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)

# -------------------------------
# ROUTES A PROPOS
# -------------------------------

@app.route("/<lang>/apropos")
def apropos(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"apropos_{lang}.html", lang=lang)

# -------------------------------
# ROUTES DON
# -------------------------------

@app.route("/<lang>/don")
def don(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"don_{lang}.html", lang=lang)

# -------------------------------
# ROUTES JEDDI
# -------------------------------

@app.route("/<lang>/jeddi")
def jeddi(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"jeddi_{lang}.html", lang=lang)

# -------------------------------
# ROUTES GRIMOIRE
# -------------------------------

@app.route("/<lang>/grimoire")
def grimoire(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"grimoire_{lang}.html", lang=lang)

# -------------------------------
# ROUTES GALERIE (DYNAMIQUE)
# -------------------------------

@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    folder = os.path.join("static", "images", "galerie")
    if not os.path.exists(folder):
        images = []
    else:
        images = [
            f for f in os.listdir(folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
        ]

    return render_template(f"galerie_{lang}.html", lang=lang, images=images)

# -------------------------------
# ROUTES LÉGENDES (TEXTE)
# -------------------------------

@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    path = os.path.join("legendes_data", f"legendes_{lang}.txt")

    if not os.path.exists(path):
        raw = ""
    else:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

    return render_template("legendes.html", lang=lang, text=raw)

# -------------------------------
# ADMIN
# -------------------------------

ADMIN_PASSWORD = os.environ.get("ADMIN_JEDDI_PASSWORD", "jedditest")

@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    path = os.path.join("legendes_data", f"legendes_{lang}.txt")

    if request.method == "POST":
        if request.form.get("password") != ADMIN_PASSWORD:
            return "Mot de passe incorrect", 403

        with open(path, "w", encoding="utf-8") as f:
            f.write(request.form.get("raw_legends", ""))

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = ""

    return render_template("admin.html", lang=lang, raw_legends=raw)

# -------------------------------
# RUN
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)
