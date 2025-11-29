from flask import Flask, g, render_template, request, redirect, url_for, flash, session
import sqlite3, os, hashlib
from functools import wraps
from datetime import datetime

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "jeddi.db")
SECRET_KEY = "change_this_secret"   # change this for production

LANGS = ["fr","en","es","de","it"]
DEFAULT_LANG = "fr"
PAGES = ["accueil","apropos","don","galerie","grimoire","jeddi","legendes","mise_en_page","ne_le_fais_pas","admin"]

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# --- Database helpers ---
def get_db():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS legends (
        id INTEGER PRIMARY KEY,
        lang TEXT,
        title TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    db.commit()
    # default admin (username: admin, password: admin) - PLEASE CHANGE
    cur.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cur.fetchone():
        h = hashlib.sha256("admin".encode()).hexdigest()
        cur.execute("INSERT INTO users(username,password_hash) VALUES (?,?)", ("admin", h))
        db.commit()

@app.teardown_appcontext
def close_db(e=None):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

# --- Auth helpers ---
def check_login(username, password):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        return False
    return row["password_hash"] == hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Vous devez être connecté pour accéder à cette page.", "error")
            return redirect(url_for("page", lang=DEFAULT_LANG, page="admin"))
        return f(*args, **kwargs)
    return decorated

# --- Context for templates ---
@app.context_processor
def inject_lang_and_page():
    lang = request.view_args.get("lang") if request.view_args else DEFAULT_LANG
    page = request.view_args.get("page") if request.view_args else "accueil"
    if lang not in LANGS:
        lang = DEFAULT_LANG
    if page not in PAGES:
        page = "accueil"
    return dict(lang=lang, current_page=page, LANGS=LANGS)

# --- Routes ---
@app.route("/")
def index():
    return redirect(url_for("page", lang=DEFAULT_LANG, page="accueil"))

@app.route("/<lang>/<page>", methods=["GET","POST"])
def page(lang, page):
    # normalize
    if lang not in LANGS:
        lang = DEFAULT_LANG
    if page not in PAGES:
        page = "accueil"

    # ADMIN login handling (admin page uses POST to login)
    if page == "admin" and request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        if check_login(username, password):
            session["logged_in"] = True
            flash(f"Connecté en tant que {username}", "info")
            return redirect(url_for("page", lang=lang, page="admin"))
        else:
            flash("Identifiants invalides", "error")

    # GRIMOIRE: submitting a legend
    if page == "grimoire" and request.method == "POST":
        title = request.form.get("title","").strip()
        content = request.form.get("content","").strip()
        if not title or not content:
            flash("Titre et contenu requis.", "error")
            return redirect(url_for("page", lang=lang, page="grimoire"))
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO legends(lang,title,content) VALUES (?,?,?)", (lang, title, content))
        db.commit()
        flash("Légende ajoutée.", "info")
        return redirect(url_for("page", lang=lang, page="grimoire"))

    # Prepare legends display for grimoire
    legends = []
    if page == "grimoire":
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM legends WHERE lang = ? ORDER BY created_at DESC", (lang,))
        legends = cur.fetchall()

    # choose template: prefer page_lang.html, fallback to page_fr.html or generic
    template_name = f"{page}_{lang}.html"
    template_path = os.path.join(app.template_folder or "templates", template_name)
    if not os.path.exists(template_path):
        # try fallback to fr version or a generic file
        alt = f"{page}_fr.html"
        if os.path.exists(os.path.join(app.template_folder or "templates", alt)):
            template_name = alt
        elif os.path.exists(os.path.join(app.template_folder or "templates", f"{page}.html")):
            template_name = f"{page}.html"
        else:
            template_name = "accueil_fr.html"
    return render_template(template_name, legends=legends)

@app.route("/admin/logout")
def logout():
    session.pop("logged_in", None)
    flash("Déconnecté.", "info")
    return redirect(url_for("page", lang=DEFAULT_LANG, page="accueil"))

# init DB on start
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
