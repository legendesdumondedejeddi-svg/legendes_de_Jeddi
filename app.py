from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Fichier où l’on stocke les légendes
DATA_FILE = "legendes.json"

# Charger les légendes
def load_legendes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Enregistrer les légendes
def save_legendes(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ------------------------------------------------------
# ROUTES PUBLIQUES
# ------------------------------------------------------

@app.route("/")
def home_default():
    return redirect(url_for("accueil"))

@app.route("/accueil")
def accueil():
    return render_template("accueil.html")

@app.route("/legendes")
def liste_legendes():
    legendes = load_legendes()
    return render_template("liste_legendes.html", legendes=legendes)

@app.route("/legende/<int:id>")
def legende_detail(id):
    legendes = load_legendes()
    for l in legendes:
        if l["id"] == id:
            return render_template("legende.html", leg=l)
    return "Légende introuvable", 404

# ------------------------------------------------------
# ADMIN
# ------------------------------------------------------

@app.route("/admin")
def admin_index():
    legendes = load_legendes()
    return render_template("admin_index.html", legendes=legendes)

@app.route("/admin/ajouter", methods=["GET", "POST"])
def admin_ajouter():
    if request.method == "POST":
        legendes = load_legendes()

        new_leg = {
            "id": len(legendes) + 1,
            "titre": request.form["titre"],
            "contenu": request.form["contenu"],
            "image": request.form["image"]
        }

        legendes.append(new_leg)
        save_legendes(legendes)

        return redirect(url_for("admin_index"))

    return render_template("admin_ajouter.html")


if __name__ == "__main__":
    app.run(debug=True)
