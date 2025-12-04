import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "jeddi_secret_key"

# Dossier upload
UPLOAD_FOLDER = "static/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mot de passe admin
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Données en mémoire (simple pour débutant)
legendes = []
# Structure :
# légende = { "id": int, "titre": str, "texte": str, "categorie": str, "image": str }


###############################
# ROUTES PUBLIQUES
###############################

@app.route("/fr/accueil")
def accueil():
    return render_template("accueil.html", title="Accueil")

@app.route("/fr/legendes")
def list_legendes():
    return render_template("liste_legendes.html", legendes=legendes, title="Légendes")

@app.route("/fr/legende/<int:leg_id>")
def legende_detail(leg_id):
    for leg in legendes:
        if leg["id"] == leg_id:
            return render_template("legende.html", legende=leg, title=leg["titre"])
    return "Légende introuvable", 404


###############################
# ROUTE ADMIN
###############################

@app.route("/fr/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        pwd = request.form.get("password")

        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect", "error")
            return redirect(url_for("admin"))

        # On récupère la légende
        titre = request.form.get("titre")
        texte = request.form.get("texte")
        categorie = request.form.get("categorie")

        # Gestion image
        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(path)
        else:
            filename = None

        legende = {
            "id": len(legendes) + 1,
            "titre": titre,
            "texte": texte,
            "categorie": categorie,
            "image": filename
        }

        legendes.append(legende)
        flash("Légende ajoutée avec succès", "success")
        return redirect(url_for("list_legendes"))

    return render_template("admin.html", title="Administration")


###############################
# REDIRECTION RACINE → ACCUEIL
###############################
@app.route("/")
def index():
    return redirect("/fr/accueil")
    @app.route("/don")
def don():
    return render_template("don.html", title="Faire un don")


if __name__ == "__main__":
    app.run(debug=True)
