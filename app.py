import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# ----------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------
ADMIN_PASSWORD = "1997.Monde-1958-Jeddi.1998"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

LANGS = ["fr", "en", "es", "de", "it"]

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ne crée PAS le dossier si déjà existant (Render déteste)
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------
# OUTIL : extensions autorisées
# ----------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------
# FORMAT DES LÉGENDES
# ----------------------------------------------------
SEPARATOR = "\n---\n"

def load_legends(lang):
    """Lit legendes_data/legendes_<lang>.txt et retourne une liste."""
    path = f"legendes_data/legendes_{lang}.txt"

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        return []

    blocks = [b.strip() for b in raw.split(SEPARATOR) if b.strip()]

    legends = []
    for block in blocks:
        lines = block.split("\n")
        title = lines[0].strip()
        image = None
        content_lines = []

        for line in lines[1:]:
            if line.startswith("==image:") and line.endswith("=="):
                image = line.replace("==image:", "").replace("==", "").strip()
            else:
                content_lines.append(line)

        content = "\n".join(content_lines).strip()
        legends.append({
            "title": title,
            "content": content,
            "image": image
        })

    return legends


def save_legend(lang, title, content, image_filename=None):
    """Sauvegarde une nouvelle légende."""
    os.makedirs("legendes_data", exist_ok=True)
    path = f"legendes_data/legendes_{lang}.txt"

    with open(path, "a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        f.write(content.strip() + "\n")
        f.write(SEPARATOR)

# ----------------------------------------------------
# ROUTES
# ----------------------------------------------------

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

# ----------------------------------------------------
# ADMIN
# ----------------------------------------------------
@app.route("/admin/<lang>", methods=["GET","POST"])
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

        # Upload de l'image
        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(filepath)
                image_filename = filename

        save_legend(lang, title, content, image_filename)

    return render_template("admin.html", lang=lang)

# ----------------------------------------------------
# GALERIE
# ----------------------------------------------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    images = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.lower().split(".")[-1] in ALLOWED_EXTENSIONS:
            images.append(filename)

    return render_template("galerie.html", lang=lang, images=images)

# ----------------------------------------------------
# LÉGENDES
# ----------------------------------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    legends = load_legends(lang)
    total = len(legends)

    page = int(request.args.get("page", 1))
    if total == 0:
        return render_template("legendes.html",
                               lang=lang,
                               legend=None,
                               page=1,
                               pages=1)

    page = max(1, min(page, total))

    return render_template("legendes.html",
                           lang=lang,
                           legend=legends[page-1],
                           page=page,
                           pages=total)

# ----------------------------------------------------
# RUN
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
