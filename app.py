import os
import json
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort, send_from_directory
)
from werkzeug.utils import secure_filename

# ---------- Configuration ----------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change_this_in_prod")

# Admin password from environment (secure)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", None)
if ADMIN_PASSWORD is None:
    # Warning visible in logs if not set — tu peux supprimer en prod si tu préfères
    app.logger.warning("ADMIN_PASSWORD not set in environment. Set ADMIN_PASSWORD for security.")

# Data file
DATA_FILE = "legendes.json"

# Upload config
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Languages supported
LANGUES = ["fr", "en", "es", "de", "it"]


# ---------- Helpers ----------
def load_legendes():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_legendes(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_id(legendes):
    return max([l["id"] for l in legendes], default=0) + 1


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Routes publiques ----------
@app.route("/")
def root():
    return redirect("/fr/accueil")


@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGUES:
        abort(404)
    return render_template("accueil.html", lang=lang)


@app.route("/<lang>/legendes")
def liste_legendes(lang):
    if lang not in LANGUES:
        abort(404)

    all_legs = load_legendes()
    # filtre par langue
    legendes_lang = [l for l in all_legs if l.get("lang") == lang]

    # filtre optionnel par catégorie ?cat=creatures
    cat = request.args.get("cat")
    if cat:
        legendes_lang = [l for l in legendes_lang if l.get("categorie") == cat]

    # pagination optionnelle ?page=1&per_page=10
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        page = 1
        per_page = 10

    total = len(legendes_lang)
    start = (page - 1) * per_page
    end = start + per_page
    page_items = legendes_lang[start:end]

    # categories disponibles pour cette langue (pour filtre)
    categories = sorted({l.get("categorie") for l in legendes_lang if l.get("categorie")})

    return render_template(
        "liste_legendes.html",
        legendes=page_items,
        lang=lang,
        page=page,
        per_page=per_page,
        total=total,
        categories=categories,
        current_cat=cat
    )


@app.route("/<lang>/legende/<int:leg_id>")
def afficher_legende(lang, leg_id):
    if lang not in LANGUES:
        abort(404)
    legendes = load_legendes()
    leg = next((l for l in legendes if l["id"] == leg_id and l.get("lang") == lang), None)
    if not leg:
        abort(404)
    return render_template("legende.html", legende=leg, lang=lang)


# Route pour servir images uploaded (généralement static fait le job)
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------- ADMIN ----------
@app.route("/<lang>/admin/login", methods=["GET", "POST"])
def admin_login(lang):
    if lang not in LANGUES:
        abort(404)
    if request.method == "POST":
        pw = request.form.get("password", "")
        if ADMIN_PASSWORD and pw == ADMIN_PASSWORD:
            session["admin"] = True
            session["admin_lang"] = lang
            flash("Connexion réussie.")
            return redirect(url_for("admin_dashboard", lang=lang))
        flash("Mot de passe incorrect.")
    return render_template("admin_login.html", lang=lang)


@app.route("/<lang>/admin/logout")
def admin_logout(lang):
    session.pop("admin", None)
    session.pop("admin_lang", None)
    flash("Déconnexion.")
    return redirect(url_for("accueil", lang=lang))


@app.route("/<lang>/admin")
def admin_dashboard(lang):
    if lang not in LANGUES:
        abort(404)
    if not session.get("admin"):
        return redirect(url_for("admin_login", lang=lang))
    legendes = [l for l in load_legendes() if l.get("lang") == lang]
    return render_template("admin_dashboard.html", legendes=legendes, lang=lang)


@app.route("/<lang>/admin/add", methods=["GET", "POST"])
def admin_add(lang):
    if lang not in LANGUES:
        abort(404)
    if not session.get("admin"):
        return redirect(url_for("admin_login", lang=lang))

    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        contenu = request.form.get("contenu", "").strip()
        categorie = request.form.get("categorie", "").strip() or None

        # image upload handling
        image_filename = ""
        file = request.files.get("image_file")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Extension de fichier non autorisée.")
                return render_template("admin_add.html", lang=lang)
            safe_name = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            file.save(save_path)
            image_filename = safe_name

        if not titre or not contenu:
            flash("Titre et contenu requis.")
            return render_template("admin_add.html", lang=lang)

        legendes = load_legendes()
        new = {
            "id": next_id(legendes),
            "lang": lang,
            "titre": titre,
            "contenu": contenu,
            "image": image_filename,
            "categorie": categorie
        }
        legendes.append(new)
        save_legendes(legendes)
        flash("Légende ajoutée.")
        return redirect(url_for("admin_dashboard", lang=lang))

    return render_template("admin_add.html", lang=lang)


@app.route("/<lang>/admin/delete/<int:leg_id>", methods=["POST"])
def admin_delete(lang, leg_id):
    if lang not in LANGUES:
        abort(404)
    if not session.get("admin"):
        return redirect(url_for("admin_login", lang=lang))
    legendes = load_legendes()
    legendes = [l for l in legendes if not (l["id"] == leg_id and l.get("lang") == lang)]
    save_legendes(legendes)
    flash("Légende supprimée.")
    return redirect(url_for("admin_dashboard", lang=lang))


# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
