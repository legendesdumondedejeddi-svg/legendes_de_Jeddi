# app.py
import os
import errno
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

# -------------------------
# CONFIGURATION
# -------------------------
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "ChangeMoiEnProd2025")
UPLOAD_FOLDER = "static/uploads"
LEGENDES_FOLDER = "legendes_data"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Créer dossiers si manquants (tolérant si existent déjà)
for d in (UPLOAD_FOLDER, LEGENDES_FOLDER, "static/images"):
    try:
        os.makedirs(d, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

app = Flask(__name__)
app.secret_key = os.environ.get("JEDDI_SECRET_KEY", "DevSecretKeyChangeMe")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

LANGS = ["fr", "en", "es", "de", "it"]

# -------------------------
# Helpers
# -------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def legend_file(lang):
    return os.path.join(LEGENDES_FOLDER, f"legendes_{lang}.txt")

def normalize_blocks(text):
    # Normalise les séparateurs pour permettre variantes
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()

# -------------------------
# Charger légendes (robuste)
# Format attendu dans le fichier:
# Title line
# (==image:filename==) optional on separate line
# content lines...
#
# (séparateur)
# (séparateur exact: une ligne vide + --- + une ligne vide ou simplement ---)
# -------------------------
def load_legends(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = normalize_blocks(f.read())
    # Split on a block separator that is either "\n\n---\n\n" or "\n---\n"
    blocks = [b.strip() for b in raw.split("\n\n---\n\n") if b.strip()]
    if len(blocks) == 0:
        # fallback: try splitting on single-line ---
        blocks = [b.strip() for b in raw.split("\n---\n") if b.strip()]
    legends = []
    for blk in blocks:
        lines = blk.split("\n")
        title = lines[0].strip() if lines else "(Sans titre)"
        image = None
        content_lines = []
        for ln in lines[1:]:
            ln = ln.strip()
            if ln.startswith("==image:") and ln.endswith("=="):
                image = ln.replace("==image:", "").replace("==", "").strip()
            else:
                content_lines.append(ln)
        content = "\n".join(content_lines).strip()
        legends.append({"title": title, "content": content, "image": image})
    # Trier A->Z par titre
    legends.sort(key=lambda x: x["title"].lower())
    return legends

def save_legend(lang, title, content, image_filename=None):
    path = legend_file(lang)
    # On écrit en utilisant la séparation recommandée: double newline + --- + double newline
    with open(path, "a", encoding="utf-8") as f:
        f.write(title.strip() + "\n")
        if image_filename:
            f.write(f"==image:{image_filename}==\n")
        f.write(content.strip() + "\n\n---\n\n")

# -------------------------
# ROUTES
# -------------------------
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
    # attention: les templates doivent exister
    tpl = f"{page}_{lang}.html"
    try:
        return render_template(tpl, lang=lang)
    except Exception as e:
        # page introuvable -> 404 friendly
        return render_template("missing_page.html", lang=lang, page=page), 404

# Admin (GET: formulaire, POST: sauvegarde)
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.")
            return redirect(url_for("admin", lang=lang))
        titre = request.form.get("titre", "").strip()
        texte = request.form.get("texte", "").strip()
        image_filename = None
        if "image" in request.files:
            image = request.files["image"]
            if image and image.filename and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                # sauvegarde
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_filename = filename
        save_legend(lang, titre, texte, image_filename)
        flash("Légende enregistrée.")
        return redirect(url_for("legendes", lang=lang))
    return render_template("admin.html", lang=lang)

# Galerie automatique
@app.route("/<lang>/galerie")
def galerie(lang):
    if lang not in LANGS:
        lang = "fr"
    files = []
    try:
        for fname in sorted(os.listdir(app.config["UPLOAD_FOLDER"])):
            if allowed_file(fname):
                files.append(fname)
    except FileNotFoundError:
        files = []
    return render_template("galerie.html", lang=lang, images=files)

# Légendes - pagination par index (1 item par page)
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"
    legends = load_legends(lang)
    if not legends:
        # Cas sans légendes
        return render_template("legendes.html", lang=lang, legend=None, page=1, pages=1)
    page = request.args.get("page", "1")
    try:
        page = int(page)
    except ValueError:
        page = 1
    total = len(legends)
    if page < 1: page = 1
    if page > total: page = total
    legend = legends[page-1]
    return render_template("legendes.html", lang=lang, legend=legend, page=page, pages=total)

# route pour servir les uploads (si besoin)
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Health check
@app.route("/sante")
def sante():
    return "ok", 200

# -------------------------
# LANCEMENT
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
