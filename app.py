import os
from flask import Flask, render_template, request, redirect, url_for, flash
from math import ceil

app = Flask(__name__)

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

SECRET_KEY = os.environ.get("JEDDI_SECRET_KEY", "DevSecretKeyChangeMe")
ADMIN_PASSWORD = os.environ.get("JEDDI_ADMIN_PASSWORD", "jeddi2025")

app.secret_key = SECRET_KEY

LANGS = ["fr", "en", "es", "de", "it"]

PAGES = ["accueil", "apropos", "jeddi", "galerie", "grimoire", "don"]

# Dossier où sont stockées les légendes (Render peut écrire ici)
SAVE_FOLDER = "legendes_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)


# ---------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------

def legend_file(lang):
    return os.path.join(SAVE_FOLDER, f"legendes_{lang}.txt")


def load_legend_texts(lang):
    """Charge les légendes formatées avec séparateur --- entre blocs."""
    path = legend_file(lang)
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = f.read()

    if not data.strip():
        return []

    blocks = data.split("\n\n---\n\n")
    legends = []

    for i, b in enumerate(blocks):
        b = b.strip()
        if not b:
            continue

        lines = b.split("\n", 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""

        legends.append({
            "id": i + 1,
            "title": title,
            "content": content
        })

    return legends


def save_legend_texts(lang, texts):
    """Sauvegarde propre du texte."""
    path = legend_file(lang)

    blocks = []
    for t in texts:
        blocks.append(f"{t['title']}\n{t['content']}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(blocks))


# ---------------------------------------
# ROUTES STATIQUES : accueil, apropos, etc.
# ---------------------------------------

for lang in LANGS:
    for page in PAGES:

        tpl = f"{page}_{lang}.html"
        route = f"/{lang}/{page}"
        endpoint = f"{page}_{lang}"

        def make_route(tpl=tpl, lg=lang):
            def route_func():
                return render_template(tpl, lang=lg)
            return route_func

        app.add_url_rule(route, endpoint, make_route())


# ---------------------------------------
# PAGE LÉGENDES AVEC PAGINATION
# ---------------------------------------

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
    legend = legends[index] if legends else {"title": "(Aucune légende)", "content": ""}

    return render_template(
        f"legendes_{lang}.html",
        lang=lang,
        page=page,
        pages=pages,
        legend_title=legend["title"],
        legend_text=legend["content"]
    )


# ---------------------------------------
# COMMENTAIRES (non utilisé mais propre)
# ---------------------------------------

@app.route("/<lang>/comment", methods=["POST"])
def comment_post(lang):
    return redirect(url_for("legendes", lang=lang))


# ---------------------------------------
# ADMINISTRATION
# ---------------------------------------

@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != ADMIN_PASSWORD:
            flash("Mot de passe incorrect.")
            return redirect(url_for("admin", lang=lang))

        raw = request.form.get("raw_legends", "")

        texts = []
        for block in raw.split("\n\n---\n\n"):
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n", 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""

            texts.append({
                "title": title,
                "content": content
            })

        save_legend_texts(lang, texts)
        flash("Légendes sauvegardées.")
        return redirect(url_for("legendes", lang=lang))

    existing = load_legend_texts(lang)
    raw = "\n\n---\n\n".join([f"{e['title']}\n{e['content']}" for e in existing])

    return render_template(f"admin_{lang}.html", lang=lang, raw_legends=raw)


# ---------------------------------------
# ROUTE DE REDIRECTION RACINE
# ---------------------------------------

@app.route("/")
def root():
    return redirect("/fr/accueil")


# ---------------------------------------
# TEST DE VIE
# ---------------------------------------

@app.route("/sante")
def sante():
    return "ok", 200


# ---------------------------------------
# LANCEMENT LOCAL
# ---------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
