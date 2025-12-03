import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "une-cle-simple"

# Dossier images
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# fichier JSON
JSON_FILE = "legendes.json"

# langues gérées
LANGUAGES = ["fr", "en", "es", "de", "it"]

# Mot de passe admin via variable d’environnement
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    app.logger.warning("ADMIN_PASSWORD not set in environment. Set ADMIN_PASSWORD for security.")


# -------------------------------
# Chargement et sauvegarde JSON
# -------------------------------
def load_legendes():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_legendes(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------------
# ROUTES MULTILINGUES
# -------------------------------

@app.route("/")
def index_redirect():
    return redirect("/fr/accueil")


@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGUAGES:
        return "Langue non supportée", 404
    return render_template("accueil.html", lang=lang)


@app.route("/<lang>/legendes")
def list_legendes(lang):
    if lang not in LANGUAGES:
        return "Langue non supportée", 404
    legendes = load_legendes()
    return render_template("liste_legendes.html", legendes=legendes, lang=lang)


@app.route("/<lang>/legende/<int:id_legende>")
def legende(lang, id_legende):
    if lang not in LANGUAGES:
        return "Langue non supportée", 404

    legendes = load_legendes()
    for l in legendes:
        if l["id"] == id_legende:
            return render_template("legende.html", legende=l, lang=lang)

    return "Légende introuvable", 404


@app.route("/<lang>/admin", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGUAGES:
        return "Langue non supportée", 404

    # Vérification mot de passe
    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.", "danger")
            return redirect(url_for("admin", lang=lang))

        titre = request.form.get("titre")
        texte = request.form.get("texte")
        categorie = request.form.get("categorie")

        image_file = request.files.get("image")
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)

        # Ajout JSON
        legendes = load_legendes()
        new_id = max([l["id"] for l in legendes], default=0) + 1

        legendes.append({
            "id": new_id,
            "titre": titre,
            "texte": texte,
            "categorie": categorie,
            "image": filename
        })

        save_legendes(legendes)
        flash("Légende ajoutée.", "success")
        return redirect(url_for("admin", lang=lang))

    legendes = load_legendes()
    categories = sorted(set([l["categorie"] for l in legendes if l.get("categorie")]))

    return render_template("admin.html", legendes=legendes, categories=categories, lang=lang)


if __name__ == "__main__":
    app.run(debug=True)
