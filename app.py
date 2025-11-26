import os
from flask import Flask, render_template, request, redirect, url_for
from math import ceil

app = Flask(__name__)

LANGS = ["fr", "en", "es", "de", "it"]

# dossier de stockage des légendes
SAVE_FOLDER = "legendes_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def legend_file(lang):
    return os.path.join(SAVE_FOLDER, f"legendes_{lang}.txt")

def load_legends(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    blocks = raw.split("\n\n---\n\n")
    legends = []

    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        lines = block.split("\n", 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else "[Contenu vide]"
        legends.append({"id": i+1, "title": title, "content": content})

    return legends


@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    # pagination
    page = int(request.args.get("page", 1))
    legends = load_legends(lang)

    total = len(legends)
    pages = max(1, ceil(total))

    if page < 1: page = 1
    if page > total: page = total

    legend = legends[page - 1] if legends else {"title": "Aucune légende", "content": ""}

    return render_template(
        "legendes.html",
        lang=lang,
        page=page,
        pages=total,
        legend=legend
    )


@app.route("/")
def root():
    return redirect("/fr/accueil")


# pages classiques
PAGES = ["accueil", "apropos", "jeddi", "galerie", "grimoire", "don"]

for lang in LANGS:
    for page in PAGES:
        route = f"/{lang}/{page}"
        tpl = f"{page}_{lang}.html"

        def make_route(tpl=tpl, lg=lang):
            def route_func():
                return render_template(tpl, lang=lg)
            return route_func

        app.add_url_rule(route, f"{page}_{lang}", make_route())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
