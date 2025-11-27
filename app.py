import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

LANGS = ["fr", "en", "es", "de", "it"]

# -------------------------
# FONCTION : Charger légendes
# -------------------------
def load_legends(lang):
    path = f"legendes_data/legendes_{lang}.txt"
    if not os.path.exists(path):
        return []

    legends = []
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n---\n")
        for block in blocks:
            if block.strip():
                try:
                    title, content = block.split("\n", 1)
                    legends.append({"title": title.strip(), "content": content.strip()})
                except:
                    pass
    return legends

# -------------------------
# FONCTION : Sauvegarder légende FR
# -------------------------
def save_legend_fr(title, content, image_filename=None):
    with open("legendes_data/legendes_fr.txt", "a", encoding="utf-8") as f:
        f.write(f"{title}\n{content}\n---\n")

# -------------------------
# ACCUEIL
# -------------------------
@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)

# -------------------------
# PAGES SIMPLES
# -------------------------
@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"{page}_{lang}.html", lang=lang)

# -------------------------
# ADMIN
# -------------------------
@app.route("/admin/<lang>", methods=["GET","POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        # Upload image
        image_file = request.files["image"]
        filename = None
        if image_file and image_file.filename:
            filename = image_file.filename
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        save_legend_fr(title, content)

        return redirect(f"/{lang}/legendes")

    return render_template("admin.html", lang=lang)

# -------------------------
# GALERIE
# -------------------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    images = []
    for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
        images.append({"filename": filename, "title": filename})

    return render_template("galerie.html", lang=lang, images=images)

# -------------------------
# LÉGENDES + PAGINATION
# -------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    page = int(request.args.get("page", 1))

    legends = load_legends(lang)
    pages = len(legends)

    if pages == 0:
        return render_template("legendes.html", lang=lang,
                               legend={"title":"Aucune légende","content":"Le grimoire attend tes mots."},
                               page=1, pages=1)

    page = max(1, min(page, pages))

    return render_template("legendes.html", lang=lang, legend=legends[page-1], page=page, pages=pages)

# -------------------------
# LANCER
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
