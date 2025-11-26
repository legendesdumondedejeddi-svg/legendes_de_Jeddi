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

from jinja2 import TemplateNotFound

@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    page = int(request.args.get("page", 1))
    legends = load_legend_texts(lang)
    total = len(legends)
    per_page = 1
    pages = max(1, ceil(total / per_page))
    if page < 1:
        page = 1
    if page > pages:
        page = pages

    index = (page - 1) * per_page
    legend = legends[index] if legends else {"title": "(Aucune légende)", "content": ""}

    # Essaye d'abord le template spécifique (legendes_fr.html etc.)
    tpl_specific = f"legendes_{lang}.html"
    try:
        return render_template(tpl_specific, lang=lang, page=page, pages=pages, legend_text=legend.get("content",""))
    except TemplateNotFound:
        # Si le template spécifique n'existe pas, utilise un template générique legendes.html
        return render_template("legendes.html", lang=lang, page=page, pages=pages, legend_text=legend.get("content",""))


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
