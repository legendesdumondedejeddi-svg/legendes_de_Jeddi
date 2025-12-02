from flask import Flask, render_template

app = Flask(__name__)

# Page d'accueil
@app.route("/")
def accueil():
    return render_template("accueil.html")

# Page : liste des légendes
@app.route("/legendes")
def liste_legendes():
    legendes = [
        {"titre": "La Forêt de Brume", "slug": "foret-brume"},
        {"titre": "Le Sceau de Jeddi", "slug": "sceau-jeddi"},
        {"titre": "La Tour des Échos", "slug": "tour-echos"},
    ]
    return render_template("liste_legendes.html", legendes=legendes)

# Page : légende individuelle
@app.route("/legende/<slug>")
def legende(slug):
    legende = {
        "titre": slug.replace("-", " ").title(),
        "contenu": """
        Voici le contenu de la légende.
        Tu pourras remplacer ce texte par ta vraie histoire,
        ou le charger depuis un fichier plus tard.
        """
    }
    return render_template("legende.html", legende=legende)

if __name__ == "__main__":
    app.run(debug=True)
