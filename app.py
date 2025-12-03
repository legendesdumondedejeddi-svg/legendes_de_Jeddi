import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = "change-this-in-production"

# Emplacement des images uploadées
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")  # Doit être défini sur Render

DATA_FILE = "legendes.json"

# Si le fichier JSON n’existe pas
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def load_legendes():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_legendes(legendes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(legendes, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return redirect(url_for("accueil"))


@app.route("/accueil")
def accueil():
    return render_template("accueil.html")


@app.route("/legendes")
def list_legendes():
    legendes = load_legendes()
    return render_template("liste_legendes.html", legendes=legendes)


@app.route("/legende/<int:id_legende>")
def legende(id_legende):
    legendes = load_legendes()
    for l in legendes:
        if l["id"] == id_legende:
            return render_template("legende.html", legende=l)
    return "Légende introuvable", 404


# Page admin liste + ajout légendes
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if ADMIN_PASSWORD is None:
        app.logger.warning("ADMIN_PASSWORD not set in environment.")

    if request.method == "POST":
        pwd = request.form.get("password")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.", "danger")
            return redirect(url_for("admin"))

        # Récupère valeurs
        titre = request.form.get("titre")
        texte = request.form.get("texte")
        categorie = request.form.get("categorie")

        # Upload image
        image_file = request.files.get("image")
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(save_path)

        # Charger les légendes existantes
        legendes = load_legendes()
        new_id = max([l["id"] for l in legendes], default=0) + 1

        new_legende = {
            "id": new_id,
            "titre": titre,
            "texte": texte,
            "categorie": categorie,
            "image": filename
        }

        legendes.append(new_legende)
        save_legendes(legendes)
        flash("Légende ajoutée.", "success")
        return redirect(url_for("admin"))

    legendes = load_legendes()
    categories = sorted(set([l["categorie"] for l in legendes if "categorie" in l]))
    return render_template("admin.html", legendes=legendes, categories=categories)
