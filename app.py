import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# ================================
# CONFIG
# ================================
ADMIN_PASSWORD = "1997.Monde-1958-Jeddi.1998"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# créer dossier upload si absent
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LANGS = ["fr", "en", "es", "de", "it"]

# ================================
# FONCTION: extensions autorisées
# ================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
def load_legends(lang):
    path = f"legendes_data/legendes_{lang}.txt"
    if not os.path.exists(path):
        return []

    legends = []

    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().strip().split("---")

        for block in blocks:
            b = block.strip()
            if not b:
                continue

            lines = b.split("\n")
            title = lines[0].strip()
            image = None
            content_lines = []

            for line in lines[1:]:
                if line.startswith("==image:") and line.endswith("=="):
                    image = line.replace("==image:", "").replace("==", "").strip()
                else:
                    content_lines.append(line)

            legends.append({
                "title": title,
                "content": "\n".join(content_lines).strip(),
                "image": image
            })

    return legends


# ================================
# SAUVEGARDER LÉGENDE FR
# ================================
def save_legend(lang, title, content, image_filename=None):
    path = f"legendes_data/legendes_{lang}.txt"
    with open(path, "a", encoding="utf-8") as f:
        f.write(title + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        f.write(content + "\n\n---\n\n")

# ================================
# ACCUEIL
# ================================
@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)

# ================================
# PAGES
# ================================
@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"

    return render_template(f"{page}_{lang}.html", lang=lang)

# ================================
# ADMIN
# ================================
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            return "Accès refusé", 403

        title = request.form.get("titre", "").strip()
        content = request.form.get("texte", "").strip()

        image_filename = None

        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_filename = filename

        save_legend(lang, title, content, image_filename)

    return render_template("admin.html", lang=lang)

# ================================
# GALERIE
# ================================
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    images = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.lower().split(".")[-1] in ALLOWED_EXTENSIONS:
            images.append(f)

    return render_template("galerie.html", lang=lang, images=images)

# ================================
# LÉGENDES (pagination)
# ================================
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    legends = load_legends(lang)

    page = int(request.args.get("page", 1))
    total = len(legends)

    if total == 0:
        return render_template("legendes.html", lang=lang, legend=None, page=1, pages=1)

    page = max(1, min(page, total))

    return render_template("legendes.html",
                           lang=lang,
                           legend=legends[page-1],
                           page=page,
                           pages=total)

# ================================
# RUN
# ================================
if __name__ == "__main__":
    app.run(debug=True)
