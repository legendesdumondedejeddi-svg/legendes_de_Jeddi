import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename

# ------------- CONFIG -------------
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "1997.Monde-1958-Jeddi.1998")
SECRET_KEY = os.environ.get("JEDDI_SECRET_KEY", "DevSecretKeyChangeMe")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
LEGENDES_FOLDER = os.path.join(BASE_DIR, "legendes_data")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LEGENDES_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

LANGS = ["fr", "en", "es", "de", "it"]

# ------------- UTILITAIRES -------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def legend_file(lang):
    return os.path.join(LEGENDES_FOLDER, f"legendes_{lang}.txt")

# Format attendu dans les fichiers : 
# Title line
# optional: ==image:filename==
# content...
# (blank line)
# ---
# (blank line)
SEPARATOR = "\n\n---\n\n"

# ------------- LOAD légendes -------------
def load_legends(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return []
    blocks = raw.split(SEPARATOR)
    legends = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].strip() if lines else "(Sans titre)"
        image = None
        content_lines = []
        for line in lines[1:]:
            if line.startswith("==image:") and "==" in line:
                # ex: ==image:foo.png==
                image = line.replace("==image:", "").replace("==", "").strip()
            else:
                content_lines.append(line)
        content = "\n".join(content_lines).strip()
        legends.append({"title": title, "content": content, "image": image})
    return legends

# ------------- SAVE légende -------------
def save_legend(lang, title, content, image_filename=None):
    path = legend_file(lang)
    block_lines = [title]
    if image_filename:
        block_lines.append(f"==image:{image_filename}==")
    block_lines.append(content)
    block = "\n".join(block_lines)
    # append with exact separator formatting
    with open(path, "a", encoding="utf-8") as f:
        if os.path.getsize(path) > 0:
            f.write("\n\n")
        f.write(block)
        f.write(SEPARATOR)

# ------------- ROUTES -------------
@app.route("/")
def root():
    return redirect("/fr/accueil")

@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"accueil_{lang}.html", lang=lang)

@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"
    # Only render known templates; guard against arbitrary file access
    allowed_pages = {"accueil","apropos","jeddi","galerie","grimoire","don","legendes","admin"}
    if page not in allowed_pages:
        abort(404)
    # For admin we want a dedicated route below; keep this for other static pages
    return render_template(f"{page}_{lang}.html", lang=lang)

# ------------- ADMIN -------------
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.", "error")
            return redirect(url_for("admin", lang=lang))

        title = request.form.get("titre", "").strip()
        content = request.form.get("texte", "").strip()
        image_filename = None

        # upload image if provided
        img = request.files.get("image")
        if img and img.filename:
            if allowed_file(img.filename):
                safe = secure_filename(img.filename)
                # add timestamp to avoid collisions
                stamp = str(int(time.time()))
                name = f"{stamp}_{safe}"
                dest = os.path.join(app.config["UPLOAD_FOLDER"], name)
                img.save(dest)
                image_filename = name
            else:
                flash("Type de fichier non autorisé pour l'image.", "error")
                return redirect(url_for("admin", lang=lang))

        # save legend
        if title or content:
            save_legend(lang, title or "(Sans titre)", content or "", image_filename)
            flash("Légende enregistrée.", "success")
        else:
            flash("Rien à enregistrer.", "warning")

        return redirect(url_for("legendes", lang=lang))

    # méthode GET : afficher formulaire + contenu actuel (preview raw)
    raw = ""
    try:
        with open(legend_file(lang), "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raw = ""
    return render_template("admin.html", lang=lang, raw_legends=raw)

# ------------- GALERIE -------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"
    files = []
    try:
        for name in sorted(os.listdir(app.config["UPLOAD_FOLDER"])):
            if allowed_file(name):
                files.append(name)
    except FileNotFoundError:
        files = []
    return render_template("galerie.html", lang=lang, images=files)

# ------------- LÉGENDES (pagination simple) -------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"
    legends = load_legends(lang)
    if not legends:
        return render_template("legendes.html", lang=lang, legend=None, page=1, pages=1)
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1
    total = len(legends)
    page = max(1, min(page, total))
    return render_template("legendes.html", lang=lang, legend=legends[page-1], page=page, pages=total)

# ------------- Static file serve (optional) -------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ------------- RUN -------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
