import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# ============================
#  CONFIGURATION
# ============================

ADMIN_PASSWORD = "1997.Monde-1958-Jeddi.1998"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

LANGS = ["fr", "en", "es", "de", "it"]

# ============================
#  INITIALISATION
# ============================

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("legendes_data", exist_ok=True)

# ============================
#  FONCTIONS UTILES
# ============================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Charger les légendes
def load_legends(lang):
    path = f"legendes_data/legendes_{lang}.txt"
    if not os.path.exists(path):
        return []

    legends = []
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n---\n")
        for block in blocks:
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n")
            title = lines[0].strip()
            content = "\n".join(lines[1:]).strip()

            image = None
            if content.startswith("==image:"):
                image = content.split("==", 2)[1].replace("image:", "").replace("==", "").strip()
                content = "\n".join(lines[2:]).strip()

            legends.append({"title": title, "content": content, "image": image})

    return legends


# Enregistrer une légende FR
def save_legend(lang, title, content, image_filename=None):
    path = f"legendes_data/legendes_{lang}.txt"

    with open(path, "a", encoding="utf-8") as f:
        f.write(title + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        f.write(content + "\n\n---\n\n")

# ============================
#  ROUTES
# ============================

@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)


@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"{page}_{lang}.html", lang=lang)


# -------------------------
#  ADMIN
# -------------------------
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":

        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            return "Accès refusé. Mot de passe incorrect.", 403

        titre = request.form.get("titre", "")
        texte = request.form.get("texte", "")

        image_filename = None

        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                image_filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        save_legend(lang, titre, texte, image_filename)

        return redirect(url_for("legendes", lang=lang))

    return render_template("admin.html", lang=lang)


# -------------------------
#  GALERIE
# -------------------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    imgs = []
    for f in os.listdir(app.config["UPLOAD_FOLDER"]):
        if allowed_file(f):
            imgs.append(f)

    return render_template("galerie.html", lang=lang, images=imgs)


# -------------------------
#  LÉGENDES + PAGINATION
# -------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    legends = load_legends(lang)
    page = int(request.args.get("page", 1))
    pages_total = len(legends)

    if pages_total == 0:
        return render_template("legendes.html", lang=lang,
            legend={"title": "Aucune légende", "content": "Le grimoire est encore vide...", "image": None},
            page=1, pages=1)

    page = max(1, min(page, pages_total))

    return render_template("legendes.html",
                           lang=lang,
                           legend=legends[page-1],
                           page=page,
                           pages=pages_total)


# -------------------------
#  LANCEMENT
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
