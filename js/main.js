async function loadLegend(key, lang = "fr") {
    try {
        const response = await fetch(`translations/${lang}/${key}.json`);
        const legend = await response.json();

        document.getElementById("lang-title").textContent = legend.title;
        document.getElementById("lang-subtitle").textContent = legend.subtitle;

        document.getElementById("lang-text").innerHTML =
            legend.text.split("\n\n").map(p => `<p>${p}</p>`).join("");

        const audio = document.getElementById("audio-player");
        audio.src = `audio/${legend.audio}`;
        audio.load();

    } catch (e) {
        console.error("Erreur chargement légende", e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadLegend("aubepin", "fr");
});
