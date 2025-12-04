import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "une_clede_securite"

# Mot de passe admin via variable d’environnement
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", None)

# Dossier images
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Fake base de données (simple dictionnaire)
LEGENDES = []


# Accueil
@app.route("/")
@app.route("/<lang>/accueil")
def accueil(lang="fr"):
    return render_template("accueil.html", title="Accueil")


# Liste des légendes
@app.route("/<lang>/legendes")
def list_legendes(lang="fr"):
    return render_template("liste_legendes.html", legendes=LEGENDES, title="Légendes")


# Admin + ajout de légende
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang="fr"):
    if not ADMIN_PASSWORD:
        flash("ADMIN_PASSWORD non défini sur Render", "error")
        return render_template("admin.html", legendes=LEGENDES, title="Admin")

    if request.method == "POST":
        password = request.form.get("password")

        if password != ADMIN_PASSWORD:
            flash("Mot de passe incorrect", "error")
            return redirect(url_for("admin", lang=lang))

        titre = request.form.get("titre")
        texte = request.form.get("texte")
        categorie = request.form.get("categorie")

        # Upload image
        image = request.files.get("image")
        filename = None

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        LEGENDES.append({
            "titre": titre,
            "texte": texte,
            "categorie": categorie,
            "image": filename
        })

        flash("Légende ajoutée", "success")
        return redirect(url_for("list_legendes", lang=lang))

    return render_template("admin.html", legendes=LEGENDES, title="Admin")


# Page Don
@app.route("/don")
@app.route("/<lang>/don")
def don(lang="fr"):
    return render_template("don.html", title="Don")


if __name__ == "__main__":
    app.run(debug=True)
