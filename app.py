import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

# PayPal masqué
PAYPAL = "patrick.letoffet@gmail.com"

# Chemin du fichier JSON des légendes
LEGENDE_FILE = "legendes.json"


def get_lang():
    """Détecte la langue depuis ?lang=xx sinon fr par défaut."""
    return request.args.get("lang", "fr")


def load_legends():
    """Charge les légendes depuis legendes.json."""
    if not os.path.exists(LEGENDE_FILE):
        return []
    with open(LEGENDE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_legends(data):
    """Sauvegarde les légendes."""
    with open(LEGENDE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ------------------------------
# Accueil
# ------------------------------
@app.route("/")
def index():
    lang = get_lang()
    return render_template(f"accueil_{lang}.html")


# ------------------------------
# À propos
# ------------------------------
@app.route("/apropos")
def apropos():
    lang = get_lang()
    return render_template(f"apropos_{lang}.html")


# ------------------------------
# Page Don
# ------------------------------
@app.route("/don")
def don():
    lang = get_lang()
    return render_template(f"don_{lang}.html", paypal=PAYPAL)


# ------------------------------
# Grimoire
# ------------------------------
@app.route("/grimoire")
def grimoire():
    lang = get_lang()
    return render_template(f"grimoire_{lang}.html")


# ------------------------------
# Liste des légendes avec pagination
# ------------------------------
@app.route("/legendes")
def liste_legendes():
    lang = get_lang()
    page = int(request.args.get("page", 1))
    legends = load_legends()

    per_page = 5
    total = len(legends)
    start = (page - 1) * per_page
    end = start + per_page

    legends_page = legends[start:end]

    return render_template(
        f"liste_legendes_{lang}.html",
        legends=legends_page,
        page=page,
        total=total,
        per_page=per_page,
        lang=lang
    )


# ------------------------------
# Affichage d’une légende par slug
# ------------------------------
@app.route("/legende/<slug>")
def legende(slug):
    legends = load_legends()
    lang = get_lang()

    for l in legends:
        if l["slug"] == slug:
            return render_template(f"legende_{lang}.html", legende=l)

    return "Légende inconnue", 404


# ------------------------------
# Admin minimal
# ------------------------------
@app.route("/admin")
def admin():
    legends = load_legends()
    return render_template("admin.html", legends=legends)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        title = request.form["title"]
        slug = request.form["slug"]
        content = request.form["content"]

        legends = load_legends()
        legends.append({"title": title, "slug": slug, "content": content})
        save_legends(legends)

        flash("Légende ajoutée !", "success")
        return redirect(url_for("admin"))

    return render_template("admin_add.html")


if __name__ == "__main__":
    app.run()
