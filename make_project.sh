#!/usr/bin/env bash
set -e

ROOT="legendes_project"
echo "Création du projet dans ./$ROOT (si existe, écrase certains fichiers) ..."

# supprime uniquement le dossier temporaire précédent si présent
rm -rf "$ROOT"
mkdir -p "$ROOT"/{templates,templates/components,static/css,static/js,static/img,data}

# requirements
cat > "$ROOT/requirements.txt" <<'PY'
Flask==3.0.2
PY

# translations.json (multilingue minimal)
cat > "$ROOT/translations.json" <<'JSON'
{
  "fr": {
    "site_title": "Légendes du Monde de Jeddi",
    "menu_home": "Accueil",
    "menu_legendes": "Légendes",
    "menu_apropos": "À propos",
    "menu_jeddi": "Jeddi",
    "menu_don": "Don",
    "don_button": "Faire un don",
    "home_title": "Bienvenue, voyageur intrépide",
    "home_intro": "<p>Bienvenue, voyageur intrépide, sur <strong>Légendes du Monde de Jeddi</strong> !</p><p>Entre donc, sans frapper — ici les portes s’ouvrent comme par enchantement...</p>",
    "apropos_title": "À propos de Légendes du Monde de Jeddi",
    "apropos_text": "Légendes du Monde de Jeddi est un projet de préservation et de partage...",
    "legendes_title": "Liste des légendes",
    "missing_title": "Page introuvable",
    "missing_text": "Cette page est perdue dans le grimoire."
  },
  "en": {
    "site_title": "Legends of Jeddi",
    "menu_home": "Home",
    "menu_legendes": "Legends",
    "menu_apropos": "About",
    "menu_jeddi": "Jeddi",
    "menu_don": "Donate",
    "don_button": "Donate",
    "home_title": "Welcome, intrepid traveler",
    "home_intro": "<p>Welcome, intrepid traveler, to <strong>Legends of Jeddi</strong>!</p>",
    "apropos_title": "About Legends of Jeddi",
    "apropos_text": "Legends of Jeddi is a preservation and sharing project...",
    "legendes_title": "List of legends",
    "missing_title": "Page not found",
    "missing_text": "This page is lost in the grimoire."
  },
  "es": {
    "site_title": "Leyendas de Jeddi",
    "menu_home": "Inicio",
    "menu_legendes": "Leyendas",
    "menu_apropos": "Acerca de",
    "menu_jeddi": "Jeddi",
    "menu_don": "Donar",
    "don_button": "Donar",
    "home_title": "Bienvenido, viajero intrépido",
    "home_intro": "<p>Bienvenido al Mundo de Jeddi...</p>",
    "apropos_title": "Sobre el proyecto",
    "apropos_text": "Este sitio preserva y comparte relatos...",
    "legendes_title": "Lista de leyendas",
    "missing_title": "Página no encontrada",
    "missing_text": "Esta página está perdida en el grimorio."
  },
  "de": {
    "site_title": "Legenden von Jeddi",
    "menu_home": "Start",
    "menu_legendes": "Legenden",
    "menu_apropos": "Über",
    "menu_jeddi": "Jeddi",
    "menu_don": "Spenden",
    "don_button": "Spenden",
    "home_title": "Willkommen, tapferer Reisender",
    "home_intro": "<p>Willkommen in der Welt von Jeddi...</p>",
    "apropos_title": "Über das Projekt",
    "apropos_text": "Dieses Projekt bewahrt und teilt Erzählungen...",
    "legendes_title": "Liste der Legenden",
    "missing_title": "Seite nicht gefunden",
    "missing_text": "Diese Seite ist im Grimoire verschollen."
  },
  "it": {
    "site_title": "Leggende di Jeddi",
    "menu_home": "Home",
    "menu_legendes": "Leggende",
    "menu_apropos": "Informazioni",
    "menu_jeddi": "Jeddi",
    "menu_don": "Dona",
    "don_button": "Dona",
    "home_title": "Benvenuto, viaggiatore intrepido",
    "home_intro": "<p>Benvenuto nel Mondo di Jeddi...</p>",
    "apropos_title": "Informazioni sul progetto",
    "apropos_text": "Questo sito conserva e condivide racconti...",
    "legendes_title": "Elenco delle leggende",
    "missing_title": "Pagina non trovata",
    "missing_text": "Questa pagina è persa nel grimorio."
  }
}
JSON

# legendes.json sample
cat > "$ROOT/data/legendes.json" <<'JSON'
{
  "legendes": [
    {
      "id": 1,
      "slug": "licorne-d-or",
      "image": "licorne.svg",
      "pays": "FR",
      "categorie": "créatures",
      "date": "1423",
      "etat": "published",
      "fr": { "titre": "La Licorne d’Or", "texte": "On raconte qu’au cœur du bois..." },
      "en": { "titre": "The Golden Unicorn", "texte": "It is said that in the heart..." }
    }
  ]
}
JSON

# app.py
cat > "$ROOT/app.py" <<'PY'
import os, json, uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET", "dev_secret_change_me")

LANGS = ["fr","en","es","de","it"]
DATA_FILE = os.path.join("data","legendes.json")
TRANSLATIONS_FILE = "translations.json"
UPLOAD_FOLDER = os.path.join("static","img","uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# load translations
with open(TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

def trans(key, lang):
    if lang not in TRANSLATIONS:
        lang = "fr"
    return TRANSLATIONS.get(lang, {}).get(key, key)

# make trans available in templates
app.jinja_env.globals.update(trans=trans)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"legendes":[]}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# root -> default language
@app.route("/")
def root():
    return redirect(url_for("accueil", lang="fr"))

@app.route("/<lang>/accueil")
def accueil(lang):
    if lang not in LANGS:
        return redirect(url_for("accueil", lang="fr"))
    latest = load_data().get("legendes", [])[:6]
    return render_template("index.html", lang=lang, latest=latest)

@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        return redirect(url_for("legendes", lang="fr"))
    data = load_data().get("legendes", [])
    # filtrer seulement les entrées qui ont la langue
    data_lang = [l for l in data if l.get(lang)]
    # tri alphabétique par titre dans la langue, puis pays
    data_lang.sort(key=lambda x: (x.get(lang, {}).get("titre","").lower(), x.get("pays","")))
    return render_template("legendes.html", lang=lang, legendes=data_lang)

@app.route("/<lang>/legende/<slug>")
def legende_detail(lang, slug):
    if lang not in LANGS:
        return redirect(url_for("legende_detail", lang="fr", slug=slug))
    data = load_data().get("legendes", [])
    item = next((l for l in data if l.get("slug")==slug), None)
    if not item or not item.get(lang):
        return render_template("missing.html", lang=lang), 404
    return render_template("legende.html", lang=lang, legende=item)

@app.route("/<lang>/a-propos")
def apropos(lang):
    if lang not in LANGS:
        return redirect(url_for("apropos", lang="fr"))
    return render_template("a_propos.html", lang=lang)

# Don: redirect to PayPal using env var (keeps email hidden)
@app.route("/don")
def don():
    paypal = os.environ.get("PAYPAL_BUSINESS","")
    if not paypal:
        return "PAYPAL_BUSINESS not configured", 500
    # use hosted button or business parameter; we use business param
    url = f"https://www.paypal.com/donate?business={paypal}&currency_code=EUR"
    return redirect(url, code=302)

# --- ADMIN simple ---
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        pwd = request.form.get("password","")
        if ADMIN_PASSWORD and pwd==ADMIN_PASSWORD:
            session["admin"]=True
            return redirect(url_for("admin_panel"))
        else:
            flash("Mot de passe incorrect","error")
    return render_template("admin_login.html")

@app.route("/admin/panel")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    data = load_data().get("legendes", [])
    return render_template("admin_panel.html", legendes=data)

@app.route("/admin/add", methods=["GET","POST"])
def admin_add():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    if request.method=="POST":
        slug = request.form.get("slug") or str(uuid.uuid4())[:8]
        pays = request.form.get("pays","FR")
        categorie = request.form.get("categorie","")
        titre = request.form.get("titre","")
        texte = request.form.get("texte","")
        lang = request.form.get("lang","fr")
        image_file = request.files.get("image")
        image_name = ""
        if image_file and image_file.filename:
            ext = image_file.filename.rsplit(".",1)[-1].lower()
            image_name = f"{slug}.{ext}"
            image_path = os.path.join(UPLOAD_FOLDER, image_name)
            image_file.save(image_path)
            # store relative path
            image_name = os.path.join("img","uploads", image_name)
        data = load_data()
        # find existing by slug
        existing = next((l for l in data.get("legendes",[]) if l.get("slug")==slug), None)
        if existing:
            existing.setdefault(lang,{})
            existing[lang]["titre"] = titre
            existing[lang]["texte"] = texte
            existing["pays"] = pays
            existing["categorie"] = categorie
            if image_name:
                existing["image"] = image_name
        else:
            new = {
                "id": max([l.get("id",0) for l in data.get("legendes",[])]+[0]) + 1,
                "slug": slug,
                "image": image_name,
                "pays": pays,
                "categorie": categorie,
                lang: {"titre": titre, "texte": texte},
                "etat": "published"
            }
            data.setdefault("legendes",[]).append(new)
        save_data(data)
        flash("Légende enregistrée","success")
        return redirect(url_for("admin_panel"))
    return render_template("admin_add.html")

@app.route("/admin/delete/<slug>", methods=["POST"])
def admin_delete(slug):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    data = load_data()
    data["legendes"] = [l for l in data["legendes"] if l.get("slug")!=slug]
    save_data(data)
    flash("Supprimé","success")
    return redirect(url_for("admin_panel"))

# static files served by Flask default; additional routes not required

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
PY

# templates/base.html
cat > "$ROOT/templates/base.html" <<'HTML'
<!doctype html>
<html lang="{{ lang if lang else 'fr' }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ trans('site_title', lang) }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  <script src="{{ url_for('static', filename='js/script.js') }}" defer></script>
</head>
<body class="site-body">
  <header class="site-header">
    <div class="banner">
      <img src="{{ url_for('static', filename='img/licorne.svg') }}" alt="Licorne" class="banner-licorne">
      <h1 class="site-title">{{ trans('site_title', lang) }}</h1>
    </div>

    <nav class="main-nav">
      <a href="{{ url_for('accueil', lang=lang) }}">{{ trans('menu_home', lang) }}</a>
      <a href="{{ url_for('legendes', lang=lang) }}">{{ trans('menu_legendes', lang) }}</a>
      <a href="{{ url_for('apropos', lang=lang) }}">{{ trans('menu_apropos', lang) }}</a>
      <a href="/don">{{ trans('menu_don', lang) }}</a>

      <div class="lang-dropdown">
        {% for code in ['fr','en','es','de','it'] %}
          <a href="{{ url_for(request.endpoint, **(request.view_args or {}), lang=code) }}">{{ code|upper }}</a>
        {% endfor %}
      </div>
    </nav>
  </header>

  <main class="page-content">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="flash-area">
          {% for category,message in messages %}
            <div class="flash {{ category }}">{{ message }}</div>
          {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
  </main>

  <footer class="site-footer">
    {% include 'components/don_button.html' %}
    <p class="contact">Contact : legendes.du.monde.de.jeddi@html.com</p>
    <p class="copyright">© Légendes du Monde de Jeddi</p>
    <img src="{{ url_for('static', filename='img/licorne_run.svg') }}" class="footer-licorne" alt="">
  </footer>
</body>
</html>
HTML

# components/don_button.html
cat > "$ROOT/templates/components/don_button.html" <<'HTML'
<div class="don-component">
  <a class="don-btn" href="/don" target="_blank">{{ trans('don_button', lang) }}</a>
</div>
HTML

# index.html
cat > "$ROOT/templates/index.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
  <article class="home-article">
    <h2>{{ trans('home_title', lang) }}</h2>
    <div class="home-intro">{{ trans('home_intro', lang) | safe }}</div>

    <section class="latest">
      <h3>Dernières légendes</h3>
      <ul class="liste-legendes">
        {% for l in latest %}
          <li>
            {% if l.get('fr') %}
              <a href="{{ url_for('legende_detail', lang=lang, slug=l.slug) }}">{{ l.get(lang, {}).get('titre', l.get('fr',{}).get('titre','')) }}</a>
              <small>({{ l.get('pays') }})</small>
            {% endif %}
          </li>
        {% endfor %}
      </ul>
    </section>
  </article>
{% endblock %}
HTML

# legendes.html
cat > "$ROOT/templates/legendes.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
  <h2>{{ trans('legendes_title', lang) }}</h2>
  <ul class="liste-legendes">
    {% for l in legendes %}
      <li class="legende-item">
        <a href="{{ url_for('legende_detail', lang=lang, slug=l.slug) }}">{{ l.get(lang,{}).get('titre', l.get('fr',{}).get('titre','(sans titre)')) }}</a>
        <span class="meta">— {{ l.get('pays','?') }} / {{ l.get('categorie','-') }}</span>
      </li>
    {% endfor %}
  </ul>
{% endblock %}
HTML

# legende.html
cat > "$ROOT/templates/legende.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
  <article class="legende-article">
    <h2>{{ legende.get(lang,{}).get('titre') }}</h2>
    {% if legende.image %}
      <img src="{{ url_for('static', filename=legende.image) }}" class="legende-image" alt="">
    {% endif %}
    <div class="legende-texte">{{ legende.get(lang,{}).get('texte') }}</div>
    <p><a href="{{ url_for('legendes', lang=lang) }}">← {{ trans('menu_legendes', lang) }}</a></p>
  </article>
{% endblock %}
HTML

# a_propos.html
cat > "$ROOT/templates/a_propos.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
  <h2>{{ trans('apropos_title', lang) }}</h2>
  <div class="apropos-text">{{ trans('apropos_text', lang) }}</div>

  <section class="jeddi">
    <h3>⚔️ Apprenez tout sur Jeddi</h3>
    <p>Jeddi est le gardien des récits anciens... (texte d'exemple)</p>
  </section>
{% endblock %}
HTML

# missing.html
cat > "$ROOT/templates/missing.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
  <h2>{{ trans('missing_title', lang) }}</h2>
  <p>{{ trans('missing_text', lang) }}</p>
{% endblock %}
HTML

# admin templates
cat > "$ROOT/templates/admin_login.html" <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><title>Admin login</title></head><body>
<h2>Admin</h2>
<form method="post">
  <label>Mot de passe: <input type="password" name="password"></label>
  <button type="submit">Connexion</button>
</form>
</body></html>
HTML

cat > "$ROOT/templates/admin_panel.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
<h2>Admin panel</h2>
<p><a href="{{ url_for('admin_add') }}">Ajouter une légende</a></p>

<ul>
  {% for l in legendes %}
    <li>{{ l.slug }} — {{ l.get('fr',{}).get('titre','') }}
      <form method="post" action="{{ url_for('admin_delete', slug=l.slug) }}" style="display:inline">
        <button type="submit">Supprimer</button>
      </form>
    </li>
  {% endfor %}
</ul>
{% endblock %}
HTML

cat > "$ROOT/templates/admin_add.html" <<'HTML'
{% extends "base.html" %}
{% block content %}
<h2>Ajouter / Mettre à jour une légende</h2>
<form method="post" enctype="multipart/form-data">
  <label>Slug: <input name="slug"></label><br>
  <label>Pays: <input name="pays" value="FR"></label><br>
  <label>Catégorie: <input name="categorie"></label><br>
  <label>Lang: <select name="lang"><option value="fr">FR</option><option value="en">EN</option></select></label><br>
  <label>Titre: <input name="titre"></label><br>
  <label>Texte: <textarea name="texte" rows="6" cols="60"></textarea></label><br>
  <label>Image: <input type="file" name="image"></label><br>
  <button type="submit">Enregistrer</button>
</form>
{% endblock %}
HTML

# components images: minimal SVGs (licorne banner + running footer sprite)
cat > "$ROOT/static/img/licorne.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120" viewBox="0 0 300 120">
  <rect width="100%" height="100%" fill="rgba(255,255,255,0)"/>
  <text x="10" y="70" font-family="serif" font-size="36" fill="#2b1a0a">🦄 Licorne</text>
</svg>
SVG

# a simple running licorne SVG (will be styled as animation in CSS)
cat > "$ROOT/static/img/licorne_run.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="60" viewBox="0 0 200 60">
  <g id="lic" transform="translate(0,0)">
    <text x="0" y="40" font-family="serif" font-size="36">🦄</text>
  </g>
</svg>
SVG

# sample grimoire and parchment SVGs
cat > "$ROOT/static/img/parchment.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect width="100%" height="100%" fill="#f4efe0"/>
  <rect x="6" y="6" width="188" height="188" fill="none" stroke="#b58a3a" stroke-width="6" rx="12"/>
</svg>
SVG

cat > "$ROOT/static/img/grimoire.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="120" viewBox="0 0 200 120">
  <rect x="5" y="10" width="190" height="100" rx="8" fill="#5b3a1a"/>
  <text x="20" y="70" font-family="serif" font-size="20" fill="#fff">Grimoire</text>
</svg>
SVG

# static css
cat > "$ROOT/static/css/style.css" <<'CSS'
/* style.css minimal et "magique" */
body.site-body {
  margin:0; font-family: Georgia, serif; background: url('/static/img/parchment.svg');
  background-size: cover; color:#2b1a0a;
}
.site-header .banner { display:flex; align-items:center; gap:18px; padding:14px; text-align:left; }
.banner-licorne { width:160px; height:auto; }
.site-title { font-size:28px; margin:0; color:#2b1a0a; }
.main-nav { display:flex; gap:18px; justify-content:center; background: rgba(0,0,0,0.35); padding:10px; }
.main-nav a { color:#fff; text-decoration:none; padding:6px 8px; border-radius:6px; }
.main-nav a:hover { background: rgba(255,255,255,0.08); }
.lang-dropdown { margin-left:20px; }
.page-content { max-width:980px; margin:22px auto; padding:12px; background: rgba(255,255,255,0.9); border-radius:8px; }
.liste-legendes { list-style:none; padding:0; }
.legende-item { padding:8px 4px; border-bottom:1px solid rgba(0,0,0,0.06); }
.legende-image { max-width:80%; display:block; margin:12px auto; }
.footer-licorne { position:fixed; bottom:6px; left:-120px; width:120px; animation: run 10s linear infinite; opacity:0.95; }
@keyframes run { 0% { left:-140px } 100% { left:110% } }

/* don button */
.don-component { margin:12px 0; text-align:center; }
.don-btn {
  display:inline-block; background: linear-gradient(135deg,#9b4dff,#ff7ab3);
  color:#fff; padding:10px 18px; border-radius:12px; text-decoration:none;
  font-weight:bold; box-shadow:0 8px 20px rgba(0,0,0,0.15);
}
.don-btn:hover { transform:translateY(-3px); }

/* admin flash */
.flash { padding:8px; border-radius:6px; margin-bottom:10px; }
.flash.error { background:#ffe9e9; color:#8a1a1a; }
.flash.success { background:#e7ffe9; color:#1a6a1b; }

/* responsive */
@media (max-width:700px) {
  .banner-licorne { width:110px; }
  .site-title { font-size:20px; }
  .page-content { margin:8px; padding:8px; }
}
CSS

# static js
cat > "$ROOT/static/js/script.js" <<'JS'
/* script.js simple */
document.addEventListener('DOMContentLoaded', function(){
  // rien de fou : si on clique la licorne en bas, on arrête l'animation
  const lic = document.querySelector('.footer-licorne');
  if(lic){
    lic.addEventListener('click', ()=> {
      if(lic.style.animationPlayState === 'paused') lic.style.animationPlayState = 'running';
      else lic.style.animationPlayState = 'paused';
    });
  }
});
JS

# create tar.gz and base64
cwd=$(pwd)
cd "$ROOT"
tar -czf ../legendes_project.tar.gz .
cd "$cwd"
base64 legendes_project.tar.gz > legendes_project.tar.gz.b64

echo "Fini. Dossier $ROOT créé."
echo "Archive: legendes_project.tar.gz"
echo "Base64: legendes_project.tar.gz.b64"
echo "Pour déployer sur Render : uploade le contenu du dossier $ROOT ou décompresse l'archive."
