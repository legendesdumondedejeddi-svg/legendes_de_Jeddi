document.addEventListener("DOMContentLoaded", () => {
    loadLegend("aubepin");
});

async function loadLegend(key) {
    try {
        const response = await fetch(`translations/fr/${key}.json`);
        const legend = await response.json();

        document.getElementById("lang-title").textContent = legend.title;
        document.getElementById("lang-subtitle").textContent = legend.subtitle;

        const textDiv = document.getElementById("lang-text");
        textDiv.innerHTML = "";

        legend.text.split("\n").forEach(line => {
            if (line.trim() !== "") {
                const p = document.createElement("p");
                p.textContent = line;
                textDiv.appendChild(p);
            }
        });

        const audio = document.getElementById("audio-player");
        audio.src = `audio/${legend.audio}`;
        audio.load();

    } catch (e) {
        console.error("Erreur chargement légende", e);
    }
}
