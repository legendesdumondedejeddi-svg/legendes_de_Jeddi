import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename

# ========== CONFIG ==========
# Ne pas laisser le mot de passe en clair en production : utilisez la variable d'environnement
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "ChangeMoiEnProd123!")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
LEGENDES_FOLDER = os.path.join(BASE_DIR, "legendes_data")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

# Create folders safely
def safe_mkdir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except FileExistsError:
        # parfois bizarrement raises; ignore
        pass
    except OSError:
        # ignore other mkdir races on some hosts
        if not os.path.isdir(path):
            raise

safe_mkdir(UPLOAD_FOLDER)
safe_mkdir(LEGENDES_FOLDER)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("JEDDI_SECRET_KEY", "dev-secret-key")

LANGS = ["fr", "en", "es", "de", "it"]
PAGES_SIMPLE = ["accueil", "apropos", "jeddi", "galerie", "grimoire", "don"]

# ========== HELPERS ==========
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def legend_file(lang):
    return os.path.join(LEGENDES_FOLDER, f"legendes_{lang}.txt")

def parse_legendes_text(text):
    """
    Parse a legends file content into list of dicts:
    Marker for image: line like ==image:filename==
    Blocks separated by a blank-line + --- + blank-line (we write this way)
    """
    blocks = [b.strip() for b in text.split("\n\n---\n\n") if b.strip()]
    legends = []
    for b in blocks:
        lines = b.splitlines()
        title = lines[0].strip() if lines else "(Sans titre)"
        image = None
        content_lines = []
        for ln in lines[1:]:
            ln = ln.rstrip("\r")
            if ln.startswith("==image:") and ln.endswith("=="):
                image = ln.replace("==image:", "").replace("==", "").strip()
            else:
                content_lines.append(ln)
        content = "\n".join(content_lines).strip()
        legends.append({"title": title, "content": content, "image": image})
    return legends

def load_legends(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_legendes_text(text)

def append_legend_to_file(lang, title, content, image_filename=None):
    path = legend_file(lang)
    with open(path, "a", encoding="utf-8") as f:
        f.write(title + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        f.write(content + "\n\n---\n\n")

# ========== ROUTES ==========
@app.route("/")
def root():
    # redirect to french accueil by default
    return redirect("/fr/accueil")

# dynamic simple pages (accueil, apropos, jeddi, grimoire, don, galerie)
@app.route("/<lang>/<page>")
def page_route(lang, page):
    if lang not in LANGS:
        lang = "fr"
    # protect against path traversal
    if page not in PAGES_SIMPLE and page != "legendes":
        abort(404)
    tpl = f"{page}_{lang}.html"
    return render_template(tpl, lang=lang)

# galerie
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"
    # images from uploads + static/images
    uploads = []
    try:
        for fname in sorted(os.listdir(app.config["UPLOAD_FOLDER"])):
            if allowed_file(fname):
                uploads.append(fname)
    except FileNotFoundError:
        uploads = []
    return render_template("galerie.html", lang=lang, images=uploads)

# legendes with pagination
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"
    legends = load_legends(lang)
    page = request.args.get("page", "1")
    try:
        page = int(page)
    except:
        page = 1
    total = len(legends)
    if total == 0:
        return render_template("legendes.html", lang=lang, legend=None, page=1, pages=1)
    page = max(1, min(page, total))
    return render_template("legendes.html", lang=lang, legend=legends[page-1], page=page, pages=total)

# admin GET shows form, POST saves legend + optional image
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            # Do not leak password in response. Simple forbidden.
            return "Accès refusé", 403

        title = request.form.get("titre", "").strip()
        content = request.form.get("texte", "").strip()
        image_filename = None

        # handle upload
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                target = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(target)
                image_filename = filename

        append_legend_to_file(lang, title or "(Sans titre)", content or "", image_filename)
        flash("Légende enregistrée.")
        return redirect(url_for("admin", lang=lang))

    # GET
    existing = load_legends(lang)
    # prepare raw content to show in textarea if wanted (admin could have different UI)
    raw = ""
    for e in existing:
        raw += e["title"] + "\n"
        if e.get("image"):
            raw += f"==image:{e['image']}==\n"
        raw += e["content"] + "\n\n---\n\n"
    return render_template("admin.html", lang=lang, raw=raw)

# serve uploaded files explicitly (flask static usually handles this, but keep safe)
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# health
@app.route("/sante")
def sante():
    return "ok", 200

if __name__ == "__main__":
    # debug True for local dev; on Render Gunicorn is used
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
