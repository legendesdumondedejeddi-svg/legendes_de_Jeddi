let currentLanguage = "fr";
let currentLegend = "aubepin";

async function loadLegend(lang, key) {
    try {
        const response = await fetch(`translations/${lang}/${key}.json`);
        const legend = await response.json();

        document.getElementById("lang-title").textContent = legend.title;
        document.getElementById("lang-subtitle").textContent = legend.subtitle;

        document.getElementById("lang-text").innerHTML =
            legend.text
                .split("\n\n")
                .map(p => `<p>${p}</p>`)
                .join("");

        const audio = document.getElementById("audio-player");
        audio.src = `audio/${legend.audio}`;
        audio.load();

    } catch (e) {
        console.error("Impossible de charger la légende.", e);
    }
}

function changeLanguage(lang) {
    currentLanguage = lang;
    loadLegend(currentLanguage, currentLegend);
}

document.addEventListener("DOMContentLoaded", () => {
    loadLegend(currentLanguage, currentLegend);
});
