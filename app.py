from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Dossier JSON des légendes
DATA_FILE = "legendes.json"

# Charger légendes
def load_legendes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Sauver légendes
def save_legendes(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


############################
# ROUTES PUBLIQUES
############################

@app.route("/")
def index():
    return redirect("/fr/accueil")

@app.route("/<lang>/accueil")
def accueil(lang):
    return render_template("accueil.html", lang=lang)

@app.route("/<lang>/legendes")
def liste_legendes(lang):
    legendes = load_legendes()
    return render_template("liste_legendes.html", legendes=legendes, lang=lang)

@app.route("/<lang>/legende/<int:id_legende>")
def legende(lang, id_legende):
    legendes = load_legendes()
    leg = next((l for l in legendes if l["id"] == id_legende), None)
    if not leg:
        return "Légende introuvable", 404
    return render_template("legende.html", legende=leg, lang=lang)


############################
# ADMIN
############################

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        flash("Mot de passe incorrect.")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    legendes = load_legendes()
    return render_template("admin_dashboard.html", legendes=legendes)

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if "admin" not in session:
        return redirect("/admin/login")

    if request.method == "POST":
        titre = request.form["titre"]
        contenu = request.form["contenu"]
        image = request.form["image"]

        legendes = load_legendes()
        next_id = max([l["id"] for l in legendes], default=0) + 1

        nouvelle = {
            "id": next_id,
            "titre": titre,
            "contenu": contenu,
            "image": image
        }

        legendes.append(nouvelle)
        save_legendes(legendes)

        flash("Légende ajoutée avec succès.")
        return redirect("/admin/dashboard")

    return render_template("admin_add_legende.html")


############################
# RUN
############################

if __name__ == "__main__":
    app.run(debug=True)
