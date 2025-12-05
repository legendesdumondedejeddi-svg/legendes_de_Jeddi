import os
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
)
from werkzeug.utils import secure_filename

# -------- CONFIG --------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev_secret_change_me")

LANGS = ["fr", "en", "es", "de", "it"]
DEFAULT_LANG = "fr"

DATA_FILE = "legendes.json"
UPLOAD_FOLDER = os.path.join("static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")  # mettre sur Render

# -------- HELPERS --------
def load_legendes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("legendes", []) if isinstance(data, dict) else data
        except json.JSONDecodeError:
            return []

def save_legendes(legendes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"legendes": legendes}, f, ensure_ascii=False, indent=2)

def get_lang_from_path_or_query(lang):
    if lang and lang in LANGS:
        return lang
    q = request.args.get("lang", DEFAULT_LANG)
    return q if q in LANGS else DEFAULT_LANG

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

def find_by_slug(legendes, slug):
    for l in legendes:
        if l.get("slug") == slug:
            return l
    return None

def next_id(legendes):
    return max([l.get("id",0) for l in legendes], default=0) + 1

# -------- ROUTES PUBLIQUES --------

@app.route("/")
def root():
    return redirect(url_for("liste_legendes", lang=DEFAULT_LANG))

@app.route("/<lang>/accueil")
def accueil(lang):
    lang = get_lang_from_path_or_query(lang)
    return render_template("accueil.html", lang=lang)

@app.route("/<lang>/legendes")
def liste_legendes(lang):
    lang = get_lang_from_path_or_query(lang)
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 8))))

    all_legs = [l for l in load_legendes() if l.get(lang)]
    total = len(all_legs)
    start = (page-1)*per_page
    page_items = all_legs[start:start+per_page]

    # categories for filter
    categories = sorted({l.get("categorie") for l in all_legs if l.get("categorie")})
    current_cat = request.args.get("cat")
    if current_cat:
        page_items = [l for l in page_items if l.get("categorie")==current_cat]

    return render_template(
        "liste_legendes.html",
        lang=lang,
        legendes=page_items,
        page=page,
        per_page=per_page,
        total=total,
        categories=categories,
        current_cat=current_cat
    )

@app.route("/<lang>/legende/<slug>")
def legende_detail(lang, slug):
    lang = get_lang_from_path_or_query(lang)
    legendes = load_legendes()
    l = find_by_slug(legendes, slug)
    if not l or not l.get(lang):
        return render_template("missing_page.html", lang=lang), 404
    # expose only the language slice to template
    return render_template("legende.html", lang=lang, legende=l)

@app.route("/<lang>/don")
def don(lang):
    lang = get_lang_from_path_or_query(lang)
    # You can later put paypal id in translations or env
    paypal_hidden = os.environ.get("PAYPAL_BUSINESS", "")  # optional
    return render_template("don.html", lang=lang, paypal=paypal_hidden)

@app.route("/<lang>/apropos")
def apropos(lang):
    lang = get_lang_from_path_or_query(lang)
    return render_template("apropos.html", lang=lang)

@app.route("/<lang>/grimoire")
def grimoire(lang):
    lang = get_lang_from_path_or_query(lang)
    return render_template("grimoire.html", lang=lang)

# -------- ADMIN SIMPLE (sessionless, simple password) --------

@app.route("/<lang>/admin", methods=["GET","POST"])
def admin(lang):
    lang = get_lang_from_path_or_query(lang)
    legendes = load_legendes()

    # Login form on the same page (simple): if POST includes password → check
    if request.method == "POST" and 'password' in request.form and 'action' not in request.form:
        pwd = request.form.get("password","")
        if not ADMIN_PASSWORD:
            flash("ADMIN_PASSWORD not set on server (security warning).", "error")
        if ADMIN_PASSWORD and pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.", "error")
        else:
            # simple way: redirect to add page
            return redirect(url_for("admin_add", lang=lang))

    return render_template("admin.html", lang=lang, legendes=legendes)

@app.route("/<lang>/admin/add", methods=["GET","POST"])
def admin_add(lang):
    lang = get_lang_from_path_or_query(lang)

    # Simple protection: require ADMIN_PASSWORD env var; if not set, allow but warn
    if not ADMIN_PASSWORD and request.method in ("GET","POST"):
        flash("WARNING: ADMIN_PASSWORD not set. Set ADMIN_PASSWORD in environment for security.", "error")

    if request.method == "POST":
        pwd = request.form.get("password","")
        if ADMIN_PASSWORD and pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.", "error")
            return redirect(url_for("admin", lang=lang))

        slug = request.form.get("slug","").strip()
        titre = request.form.get("titre","").strip()
        texte = request.form.get("texte","").strip()
        categorie = request.form.get("categorie","").strip()
        # image upload
        file = request.files.get("image")
        image_filename = ""
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Extension de fichier non autorisée.", "error")
                return redirect(url_for("admin_add", lang=lang))
            if file:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                image_filename = filename

        if not slug or not titre or not texte:
            flash("Slug, titre et texte requis.", "error")
            return redirect(url_for("admin_add", lang=lang))

        legendes = load_legendes()
        existing = find_by_slug(legendes, slug)
        if existing:
            # replace or add language content inside existing entry
            existing.setdefault(lang, {})
            existing[lang]["titre"] = titre
            existing[lang]["texte"] = texte
            if image_filename:
                existing["image"] = image_filename
            existing["categorie"] = categorie or existing.get("categorie")
            existing["date"] = existing.get("date") or datetime.utcnow().isoformat()
            flash("Légende mise à jour pour la langue " + lang, "success")
        else:
            new = {
                "id": next_id(legendes),
                "slug": slug,
                "image": image_filename,
                "categorie": categorie or None,
                "date": datetime.utcnow().isoformat(),
                lang: {
                    "titre": titre,
                    "texte": texte
                },
                "etat": "published"
            }
            legendes.append(new)
            flash("Nouvelle légende ajoutée.", "success")
        save_legendes(legendes)
        return redirect(url_for("liste_legendes", lang=lang))

    return render_template("admin_add.html", lang=lang)

@app.route("/<lang>/admin/delete/<slug>", methods=["POST"])
def admin_delete(lang, slug):
    lang = get_lang_from_path_or_query(lang)
    if ADMIN_PASSWORD and request.form.get("password","") != ADMIN_PASSWORD:
        flash("Mot de passe incorrect.", "error")
        return redirect(url_for("admin", lang=lang))
    legendes = load_legendes()
    legendes = [l for l in legendes if l.get("slug") != slug]
    save_legendes(legendes)
    flash("Légende supprimée.", "success")
    return redirect(url_for("admin", lang=lang))

# serve uploaded images (optional helper)
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 404
@app.errorhandler(404)
def page_not_found(e):
    lang = request.view_args.get("lang") if request.view_args else DEFAULT_LANG
    return render_template("missing_page.html", lang=lang), 404

# -------- RUN --------
if __name__ == "__main__":
    app.run(debug=True)
