import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# --------------------------------------------------------
# CONFIGURATION GÉNÉRALE
# --------------------------------------------------------
ADMIN_PASSWORD = "1997.Monde-1958-Jeddi.1998"
LANGS = ["fr", "en", "es", "de", "it"]

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Création des dossiers si manquants (sans erreur si existant)
os.makedirs("legendes_data", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

# --------------------------------------------------------
# Vérifier si fichier autorisé
# --------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

#import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# (le reste de ton fichier app.py reste pareil, y compris config, ADMIN_PASSWORD, UPLOAD_FOLDER, ALLOWED_EXTENSIONS...)

# ---------- Fonctions corrigées pour lire / écrire les légendes ----------
SEPARATOR = "\n---\n"   # <- IMPORTANT : utiliser exactement ce séparateur partout

def load_legends(lang):
    """
    Lit legendes_data/legendes_<lang>.txt et renvoie une liste de dicts :
    { "title": ..., "content": ..., "image": <filename or None> }
    """
    path = f"legendes_data/legendes_{lang}.txt"
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        return []

    # Séparer en blocs propres
    raw_blocks = [b.strip() for b in raw.split(SEPARATOR) if b.strip()]
    legends = []
    for block in raw_blocks:
        lines = [ln for ln in block.splitlines()]
        if not lines:
            continue
        title = lines[0].strip()
        image = None
        content_lines = []
        for ln in lines[1:]:
            ln_stripped = ln.strip()
            if ln_stripped.startswith("==image:"):
                # format attendu: ==image:nomfichier.ext==
                img = ln_stripped.replace("==image:", "").replace("==", "").strip()
                if img:
                    image = img
            else:
                content_lines.append(ln)
        content = "\n".join(content_lines).strip()
        legends.append({"title": title, "content": content, "image": image})
    return legends

def save_legend(lang, title, content, image_filename=None):
    """
    Ajoute une légende à legendes_data/legendes_<lang>.txt
    (n'écrase pas le fichier, ajoute à la fin)
    """
    os.makedirs("legendes_data", exist_ok=True)
    path = f"legendes_data/legendes_{lang}.txt"
    with open(path, "a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")
        if image_filename:
            # ligne image : exactement ce format
            f.write(f"==image:{image_filename}==\n")
        f.write(content.strip() + "\n")
        f.write(SEPARATOR)

# --------------------------------------------------------
# ACCUEIL
# --------------------------------------------------------
@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)

# --------------------------------------------------------
# PAGES SIMPLES (apropos, jeddi, galerie, etc.)
# --------------------------------------------------------
@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"

    return render_template(f"{page}_{lang}.html", lang=lang)

# --------------------------------------------------------
# PAGE ADMIN
# --------------------------------------------------------
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

        # Enregistrement image si fournie
        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_filename = filename

        save_legend(lang, title, content, image_filename)

    return render_template("admin.html", lang=lang)

# --------------------------------------------------------
# GALERIE
# --------------------------------------------------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"

    # lister images
    images = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().split(".")[-1] in ALLOWED_EXTENSIONS
    ]

    return render_template("galerie.html", lang=lang, images=images)

# --------------------------------------------------------
# LÉGENDES + PAGINATION
# --------------------------------------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    legends = load_legends(lang)
    total = len(legends)

    page = int(request.args.get("page", 1))

    if total == 0:
        return render_template("legendes.html", lang=lang, legend=None, page=1, pages=1)

    if page < 1:
        page = 1
    if page > total:
        page = total

    legend = legends[page - 1]

    return render_template("legendes.html",
                           lang=lang,
                           legend=legend,
                           page=page,
                           pages=total)

# --------------------------------------------------------
# RUN LOCAL
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
