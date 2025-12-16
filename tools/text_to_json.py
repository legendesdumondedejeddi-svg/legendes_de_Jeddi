import json
from pathlib import Path

LANGS = ["fr", "en", "de", "es", "it"]
LEGEND_ID = "aubepin"

def clean(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace('"', '\\"')
    text = text.replace("\n\n", "\\n\\n")
    text = text.replace("\n", "\\n")
    return text

source = Path("../legends/aubepin.txt").read_text(encoding="utf-8")
cleaned = clean(source)

out = Path("../translations")
out.mkdir(exist_ok=True)

for lang in LANGS:
    data = {
        LEGEND_ID: {
            "title": "",
            "subtitle": "",
            "text": cleaned,
            "audio": f"{LEGEND_ID}_{lang}.mp3",
            "country": ""
        }
    }

    (out / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

print("✔ Traductions générées. Le monde ne s’est pas effondré.")

