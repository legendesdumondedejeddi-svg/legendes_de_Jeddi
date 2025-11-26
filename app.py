from flask import Flask, render_template, request, redirect, url_for, flash
import os
from math import ceil

app = Flask(__name__)

@app.route("/admin/<lang>", methods=["GET","POST"])
def admin(lang):
    if lang not in LANGS:
        lang = "fr"

    # -------------------------------------------
    # Nouvelle sécurité : mot de passe dans Render
    # -------------------------------------------
    real_pwd = os.environ.get("ADMIN_JEDDI_PASSWORD", "CHANGER_CECI")

    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd != real_pwd:
            flash("Mot de passe incorrect.")
            return redirect(url_for("admin", lang=lang))

        raw = request.form.get("raw_legends", "")
        texts = []
        for block in raw.split("\n\n---\n\n"):
            b = block.strip()
            if not b: 
                continue
            lines = b.split("\n", 1)
            title = lines[0]
            content = lines[1] if len(lines) > 1 else ""
            texts.append({"title": title, "content": content})

        save_legend_texts(lang, texts)
        flash("Légendes sauvegardées.")
        return redirect(url_for("legendes", lang=lang))

    existing = load_legend_texts(lang)
    raw = "\n\n---\n\n".join([f"{e['title']}\n{e['content']}" for e in existing])
    return render_template(f"admin_{lang}.html", lang=lang, raw_legends=raw)
