import os
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
)
from werkzeug.utils import secure_filename

# ------------- CONFIG -------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "change_this_for_prod")

LANGS = ["fr", "en", "es", "de", "it"]
DEFAULT_LANG = "fr"

DATA_FILE = "legendes.json"
TRANSLATIONS_DIR = "translations"

UPLOAD_FOLDER = os.path.join("static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")  # must be set in env for security
PAYPAL_BUSINESS = os.environ.get("PAYPAL_BUSINESS", "patrick.letoffet@gmail.com")  # hidden on server

# ------------- HELPERS -------------
def load_translations(lang):
    path = os.path.join(TRANSLATIONS_DIR, f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_legendes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("legendes", []) if isinstance(data, dict) else data

def save_legendes(legendes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"legendes": legendes}, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def next_id(legendes):
    return max([l.get("id", 0) for l in legendes], default=0) + 1

def get_lang_or_default(lang):
    return lang if lang in LANGS else DEFAULT_LANG

def find_by_slug(legendes, slug):
    for l in legendes:
        if l.get("slug") == slug:
            return l
    return None

# Context for templates: translations & contact email
@app.context_processor
def inject_globals():
    # try to determine lang from view args or query
    lang = request.view_args.get("lang") if request.view_args else request.args.get("lang", DEFAULT_LANG)
    if lang not in LANGS:
        lang = DEFAULT_LANG
    t = load_translations(lang)
    return dict(t=t, contact_email="legendes.du.monde.de.jeddi@gmail.com")

# ------------- ROUTES -------------
@app.route("/")
def root():
    # default redirect to french accueil
    return redirect(url_for("accueil", lang=DEFAULT_LANG))

@app.route("/<lang>/accueil")
def accueil(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    return render_template("accueil.html", lang=lang, t=t)

@app.route("/<lang>/don")
def don(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    # PAYPAL_BUSINESS provided by env; not exposed in templates except as a hidden value in forms
    return render_template("don.html", lang=lang, t=t, paypal_business=PAYPAL_BUSINESS)

@app.route("/<lang>/apropos")
def apropos(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    return render_template("apropos.html", lang=lang, t=t)

@app.route("/<lang>/grimoire")
def grimoire(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    return render_template("grimoire.html", lang=lang, t=t)

@app.route("/<lang>/legendes")
def liste_legendes(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)

    all_legs = load_legendes()
    # filter only entries that have content for this language
    legs_lang = [l for l in all_legs if l.get(lang)]
    # optional category filter
    cat = request.args.get("cat")
    if cat:
        legs_lang = [l for l in legs_lang if l.get("categorie") == cat]

    # pagination
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    try:
        per_page = max(1, min(50, int(request.args.get("per_page", 8))))
    except ValueError:
        per_page = 8

    total = len(legs_lang)
    start = (page - 1) * per_page
    page_items = legs_lang[start:start + per_page]

    categories = sorted({l.get("categorie") for l in legs_lang if l.get("categorie")})

    return render_template(
        "liste_legendes.html",
        lang=lang, t=t,
        legendes=page_items,
        page=page, per_page=per_page, total=total,
        categories=categories, current_cat=cat
    )

@app.route("/<lang>/legende/<slug>")
def legende_detail(lang, slug):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    legs = load_legendes()
    l = find_by_slug(legs, slug)
    if not l or not l.get(lang):
        return render_template("missing_page.html", lang=lang, t=t), 404
    # pass the whole object; template will pick l[lang]
    return render_template("legende.html", lang=lang, t=t, legende=l)

# ------------- ADMIN (simple) -------------
@app.route("/<lang>/admin", methods=["GET", "POST"])
def admin_dashboard(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    legendes = load_legendes()
    # login on same page simple flow: POST with password will redirect to add
    if request.method == "POST":
        pw = request.form.get("password", "")
        if not ADMIN_PASSWORD:
            flash("ADMIN_PASSWORD not set on server. Admin is not secure.", "error")
        if ADMIN_PASSWORD and pw != ADMIN_PASSWORD:
            flash(t.get("admin_badpw", "Mot de passe incorrect"), "error")
        else:
            return redirect(url_for("admin_add", lang=lang))
    return render_template("admin.html", lang=lang, t=t, legendes=legendes)

@app.route("/<lang>/admin/add", methods=["GET", "POST"])
def admin_add(lang):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if ADMIN_PASSWORD and pwd != ADMIN_PASSWORD:
            flash(t.get("admin_badpw", "Mot de passe incorrect"), "error")
            return redirect(url_for("admin_dashboard", lang=lang))

        slug = request.form.get("slug", "").strip()
        titre = request.form.get("titre", "").strip()
        texte = request.form.get("texte", "").strip()
        categorie = request.form.get("categorie", "").strip() or None

        # image handling
        image_filename = ""
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash(t.get("err_bad_ext", "Extension non autorisée"), "error")
                return redirect(url_for("admin_add", lang=lang))
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            image_filename = filename

        if not slug or not titre or not texte:
            flash(t.get("err_required", "Slug, titre et texte requis"), "error")
            return redirect(url_for("admin_add", lang=lang))

        legendes = load_legendes()
        existing = find_by_slug(legendes, slug)
        now = datetime.utcnow().isoformat()
        if existing:
            # update language slice
            existing.setdefault(lang, {})
            existing[lang]["titre"] = titre
            existing[lang]["texte"] = texte
            if image_filename:
                existing["image"] = image_filename
            existing["categorie"] = categorie or existing.get("categorie")
            existing["date"] = existing.get("date") or now
            flash(t.get("admin_updated", "Légende mise à jour"), "success")
        else:
            new = {
                "id": next_id(legendes),
                "slug": slug,
                "image": image_filename,
                "categorie": categorie,
                "date": now,
                lang: {
                    "titre": titre,
                    "texte": texte
                },
                "etat": "published"
            }
            legendes.append(new)
            flash(t.get("admin_added", "Nouvelle légende ajoutée"), "success")
        save_legendes(legendes)
        return redirect(url_for("liste_legendes", lang=lang))

    return render_template("admin_add.html", lang=lang, t=t)

@app.route("/<lang>/admin/delete/<slug>", methods=["POST"])
def admin_delete(lang, slug):
    lang = get_lang_or_default(lang)
    t = load_translations(lang)
    if ADMIN_PASSWORD and request.form.get("password", "") != ADMIN_PASSWORD:
        flash(t.get("admin_badpw", "Mot de passe incorrect"), "error")
        return redirect(url_for("admin_dashboard", lang=lang))
    legendes = load_legendes()
    legendes = [l for l in legendes if l.get("slug") != slug]
    save_legendes(legendes)
    flash(t.get("admin_deleted", "Légende supprimée"), "success")
    return redirect(url_for("admin_dashboard", lang=lang))

# serve uploaded images (optional)
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 404
@app.errorhandler(404)
def page_not_found(e):
    # try to pick lang from request args
    lang = request.view_args.get("lang") if request.view_args else request.args.get("lang", DEFAULT_LANG)
    t = load_translations(lang if lang in LANGS else DEFAULT_LANG)
    return render_template("missing_page.html", lang=lang, t=t), 404

# ------------- RUN -------------
if __name__ == "__main__":
    app.run(debug=True)
