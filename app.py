# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from math import ceil

# ------------------------
# Configuration
# ------------------------
SECRET_KEY = os.environ.get("JEDDI_SECRET_KEY", "DevSecretKeyChangeMe")
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "1997.Monde-1958-Jeddi.1998")
UPLOAD_FOLDER = os.environ.get("JEDDI_UPLOAD_FOLDER", "static/uploads")
LEGENDS_FOLDER = os.environ.get("JEDDI_LEGENDS_FOLDER", "legendes_data")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# safe creation of directories even if a file with same name exists
def safe_makedirs(path):
    if os.path.exists(path) and not os.path.isdir(path):
        try:
            os.remove(path)
        except Exception:
            pass
    os.makedirs(path, exist_ok=True)

safe_makedirs(UPLOAD_FOLDER)
safe_makedirs(LEGENDS_FOLDER)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

LANGS = ["fr", "en", "es", "de", "it"]
BLOCK_SEP = "\n\n---\n\n"   # exact separator used in files

# ------------------------
# Helpers
# ------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def legend_file_path(lang):
    return os.path.join(LEGENDS_FOLDER, f"legendes_{lang}.txt")

def load_legends(lang):
    """Return list of {title, content, image} from legends file (preserve order)."""
    path = legend_file_path(lang)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return []
    blocks = raw.split(BLOCK_SEP)
    legends = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        # first line = title, then optional image marker line(s), then content
        lines = b.splitlines()
        title = lines[0].strip()
        image = None
        content_lines = []
        for line in lines[1:]:
            if line.startswith("==image:") and line.endswith("=="):
                image = line.replace("==image:", "").replace("==", "").strip()
            else:
                content_lines.append(line)
        content = "\n".join(content_lines).strip()
        legends.append({"title": title, "content": content, "image": image})
    return legends

def save_legend(lang, title, content, image_filename=None):
    """Append one legend to the legends file using BLOCK_SEP format."""
    path = legend_file_path(lang)
    # normalise newlines
    title = title.strip()
    content = content.strip()
    with open(path, "a", encoding="utf-8") as f:
        f.write(title + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        if content:
            f.write(content + "\n")
        f.write(BLOCK_SEP)

# ------------------------
# Routes: static helper
# ------------------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ------------------------
# Home redirect
# ------------------------
@app.route("/")
def root():
    return redirect("/fr/accueil")

# ------------------------
# Simple pages handler (accueil, apropos, jeddi, galerie, don)
# expects templates like accueil_fr.html, apropos_fr.html etc.
# ------------------------
@app.route("/<lang>/<page>")
def page(lang, page):
    if lang not in LANGS:
        lang = "fr"
    tpl = f"{page}_{lang}.html"
    try:
        return render_template(tpl, lang=lang)
    except Exception as e:
        # helpful debug message in logs and a friendly 404 for the user
        app.logger.exception("Template missing or template error for %s", tpl)
        return ("Page introuvable ou erreur de template.", 404)

# ------------------------
# Admin: write legend + optional image upload
# ------------------------
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

        # file upload
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(save_path)
                image_filename = filename

        # save legend
        if title or content:
            save_legend(lang, title or "(Titre manquant)", content, image_filename)
            flash("Légende enregistrée.", "success")
        else:
            flash("Titre ou texte manquant.", "error")

        return redirect(url_for("admin", lang=lang))

    # GET -> show admin (form)
    return render_template("admin.html", lang=lang)

# ------------------------
# Gallery
# ------------------------
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"
    files = []
    try:
        for fn in sorted(os.listdir(app.config["UPLOAD_FOLDER"])):
            if allowed_file(fn):
                files.append(fn)
    except FileNotFoundError:
        files = []
    return render_template("galerie.html", lang=lang, images=files)

# ------------------------
# Legendes with pagination
# ------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    legends = load_legends(lang)
    total = len(legends)
    page = request.args.get("page", "1")
    try:
        page = int(page)
    except:
        page = 1

    if total == 0:
        # render a friendly empty page
        return render_template("legendes.html", lang=lang,
                               legend=None, page=1, pages=1)

    pages = max(1, total)
    if page < 1: page = 1
    if page > pages: page = pages

    legend = legends[page-1]
    return render_template("legendes.html", lang=lang, legend=legend, page=page, pages=pages)

# ------------------------
# Health check
# ------------------------
@app.route("/sante")
def sante():
    return "ok", 200

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
