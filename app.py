from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

def load_translations(lang="fr"):
    with open(f"translations/{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def accueil():
    t = load_translations("fr")
    return render_template("accueil.html", t=t)

@app.route("/legendes")
def legendes():
    t = load_translations("fr")
    return render_template("legendes.html", t=t)

@app.route("/apropos")
def apropos():
    t = load_translations("fr")
    return render_template("apropos.html", t=t)

@app.route("/don")
def don():
    t = load_translations("fr")
    return render_template("don.html", t=t)

if __name__ == "__main__":
    app.run(debug=True)
