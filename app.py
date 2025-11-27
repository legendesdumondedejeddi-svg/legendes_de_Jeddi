import os
from flask import Flask, render_template, request, redirect, url_for
from math import ceil

app = Flask(__name__)

LANGS = ["fr", "en", "es", "de", "it"]

# dossier où les légendes sont stockées
SAVE_FOLDER = "legendes_data"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def legend_file(lang):
    return os.path.join(SAVE_FOLDER, f"legendes_{lang}.txt")

def load_legends(lang):
    path = legend_file(lang)
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n---\n\n")

        legends = []
        for i, block in enumerate(blocks):
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n", 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""

            legends.append({
                "id": i + 1,
                "title": title,
                "content": content
            })

        return legends

def save_legends(lang, legends):
    path = legend_file(lang)

    with open(path, "w", encoding="utf-8") as f:
        blocks = []
        for L in legends:
            blocks.append(f"{L['title']}\n{L['content']}")
        f.write("\n\n---\n\n".join(blocks))

# ROUTES
@app.route("/")
def root():
    return redirect("/fr/accueil")

@app.route("/<lang>/<page>")
def pages(lang, page):
    if lang not in LANGS:
        lang = "fr"
    return render_template(f"{page}_{lang}.html", lang=lang)

# PAGE : LÉGENDES
@app.route("/<lang>/legendes")
def legendes(lang):
    if lang not in LANGS:
        lang = "fr"

    page = int(request.args.get("page", 1))

    legends = load_legends(lang)
    total = len(legends)
    per_page = 1
    pages = max(1, ceil(total / per_page))

    if page < 1:
        page = 1
    if page > pages:
        page = pages

    index = (page - 1)

    current = legends[index] if legends else {
        "title": "(Aucune légende)",
        "content": ""
    }

    return render_template(
        "legendes.html",
        lang=lang,
        legend=current,
        page=page,
        pages=pages
    )

# ADMIN : écrire les légendes
@app.route("/admin/<lang>", methods=["GET", "POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    file_path = legend_file(lang)

    if request.method == "POST":
        raw = request.form.get("raw_legends", "")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw)

        return redirect(f"/{lang}/legendes")

    # lecture pour affichage
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = ""

    return render_template("admin.html", lang=lang, raw_legends=raw)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
