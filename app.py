# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from math import ceil

# -------------------------
# Configuration
# -------------------------
SECRET_KEY = os.environ.get("JEDDI_SECRET_KEY", "DevSecretKeyChangeMe")
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "ChangeMoiEnProd")
UPLOAD_FOLDER = "static/legendes_images"
SAVE_FOLDER = "legendes_data"
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAVE_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

# -------------------------
# Langues et pages
# -------------------------
LANGS = ["fr", "en", "es", "de", "it"]
PAGES = ["accueil", "apropos", "jeddi", "galerie", "don"]

def legend_file(lang):
    return os.path.join(SAVE_FOLDER, f"legendes_{lang}.txt")

def load_legend_texts(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n---\n\n")
        legends = []
        for i, b in enumerate(blocks):
            b = b.strip()
            if not b:
                continue
            lines = b.split("\n", 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""
            # try to find matching image file (safe name)
            safe = secure_filename(title).lower().replace(" ", "_")
            image = None
            for ext in ALLOWED_EXT:
                candidate = f"{safe}.{ext}"
                candidate_path = os.path.join(app.config["UPLOAD_FOLDER"], candidate)
                if os.path.exists(candidate_path):
                    image = url_for("static", filename=f"legendes_images/{candidate}")
                    break
            legends.append({"id": i+1, "title": title, "content": content, "image": image})
        return legends

def save_legend_texts(lang, texts):
    path = legend_file(lang)
    with open(path, "w", encoding="utf-8") as f:
        blocks = []
        for t in texts:
            blocks.append(f"{t['title']}\n{t['content']}")
        f.write("\n\n---\n\n".join(blocks))

# -------------------------
# Routes statiques multi-langues
# -------------------------
for lang in LANGS:
    for page in PAGES:
        template_name = f"{page}_{lang}.html"
        route = f"/{lang}/{page}"
        def make_route(tpl=template_name, lg=lang):
            def route_func():
                # if template missing, Flask will raise TemplateNotFound -> dev will see logs
                return render_template(tpl, lang=lg)
            return route_func
        endpoint = f"{page}_{lang}"
        app.add_url_rule(route, endpoint, make_route())

# -------------------------
# Légendes (liste / lecture)
# -------------------------
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"
    page = int(request.args.get("page", 1))
    legends = load_legend_texts(lang)
    total = len(legends)
    per_page = 1
    pages = max(1, ceil(total / per_page))
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    index = (page - 1) * per_page
    legend = legends[index] if legends else {"title":"(Aucune légende)","content":""}
    comments = []  # kept simple (no persistence)
    return render_template("legendes.html", lang=lang, page=page, pages=pages, legend=legend, comments=comments)

# -------------------------
# Commentaires simple (non persistants)
# -------------------------
comments_store = []
@app.route("/<lang>/comment", methods=["POST"])
def comment_post(lang):
    author = request.form.get("author", "Anonyme").strip()
    text = request.form.get("comment", "").strip()
    if text:
        comments_store.append({"lang": lang, "author": author, "text": text})
        flash("Merci, commentaire enregistré.")
    return redirect(url_for("legendes", lang=lang))

# -------------------------
# Admin : éditer + upload image
# -------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.")
            return redirect(url_for("admin", lang=lang))

        # handle upload image
        file = request.files.get("image")
        title_for_image = request.form.get("title_for_image", "").strip()
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Type de fichier non autorisé (png/jpg/gif/webp).")
            else:
                # use title_for_image if provided, else filename base
                if title_for_image:
                    base = secure_filename(title_for_image).lower().replace(" ", "_")
                    ext = file.filename.rsplit(".", 1)[1].lower()
                    filename = f"{base}.{ext}"
                else:
                    filename = secure_filename(file.filename)
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)
                flash(f"Image sauvegardée : {filename}")

        # handle legends text
        raw = request.form.get("raw_legends", "")
        texts = []
        for block in raw.split("\n\n---\n\n"):
            b = block.strip()
            if not b:
                continue
            lines = b.split("\n", 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""
            texts.append({"title": title, "content": content})
        save_legend_texts(lang, texts)
        flash("Légendes sauvegardées.")
        return redirect(url_for("legendes", lang=lang))

    existing = load_legend_texts(lang)
    raw = "\n\n---\n\n".join([f"{e['title']}\n{e['content']}" for e in existing])
    return render_template("admin.html", lang=lang, raw_legends=raw)

# -------------------------
# Root + santé
# -------------------------
@app.route("/")
def root():
    return redirect("/fr/accueil")

@app.route("/sante")
def sante():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
