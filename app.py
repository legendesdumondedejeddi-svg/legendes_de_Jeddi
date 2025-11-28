def load_legends(lang):
    path = f"legendes_data/legendes_{lang}.txt"
    if not os.path.exists(path):
        return []

    legends = []
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n---\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) == 0:
                continue

            title = lines[0].strip()
            image = None
            content_lines = []

            for line in lines[1:]:
                if line.startswith("==image:"):
                    image = line.replace("==image:", "").replace("==", "").strip()
                else:
                    content_lines.append(line)

            content = "\n".join(content_lines).strip()

            legends.append({
                "title": title,
                "content": content,
                "image": image
            })

    return legends
