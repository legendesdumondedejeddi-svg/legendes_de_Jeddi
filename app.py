from flask import Flask, render_template, request, session, url_for, redirect
import json

app = Flask(__name__)
app.secret_key = "jeddi"

# Charger les traductions
with open("translations.json", "r", encoding="utf8") as f:
    translations = json.load(f)

def get_lang():
    return request.args.get("lang", "fr")

def T(lang):
    return translations.get(lang, translations["fr"])

@app.route("/")
def home():
    lang = get_lang()
    return render_template("home.html", t=T(lang), lang=lang, title=T(lang)["title_home"])

@app.route("/about")
def about():
    lang = get_lang()
    return render_template("about.html", t=T(lang), lang=lang, title=T(lang)["title_about"])

@app.route("/don")
def don():
    lang = get_lang()
    return render_template("don.html", t=T(lang), lang=lang, title=T(lang)["title_don"])

@app.route("/grimoire")
def grimoire():
    lang = get_lang()
    return render_template("grimoire.html", t=T(lang), lang=lang, title=T(lang)["title_grimoire"])

@app.route("/legendes")
def liste_legendes():
    lang = get_lang()
    return render_template("liste_legendes.html", t=T(lang), lang=lang, title=T(lang)["title_legendes"])

@app.route("/legende/<slug>")
def legende(slug):
    lang = get_lang()
    return render_template("legende.html", slug=slug, t=T(lang), lang=lang, title=T(lang)["title_legendes"])
