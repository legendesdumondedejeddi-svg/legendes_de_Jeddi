/* =========================
   CONFIG
   ========================= */

let currentLanguage = "fr";
let currentLegendKey = "aubepin"; // légende par défaut

/* =========================
   CHARGEMENT D’UNE LÉGENDE
   ========================= */

async function loadLegend(lang, key) {
    try {
        const response = await fetch(`translations/${lang}/${key}.json`);
        if (!response.ok) throw new Error("Fichier introuvable");
        const legend = await response.json();
        displayLegend(legend);
    } catch (error) {
        console.error("Erreur chargement légende :", error);
    }
}

/* =========================
   AFFICHAGE
   ========================= */

function displayLegend(legend) {
    document.getElementById("lang-title").textContent = legend.title || "";
    document.getElementById("lang-subtitle").textContent = legend.subtitle || "";

    const textContainer = document.getElementById("lang-text");
    textContainer.innerHTML = legend.text
        .split("\n\n")
        .map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`)
        .join("");

    const audioPlayer = document.getElementById("audio-player");
    audioPlayer.src = legend.audio ? `audio/${legend.audio}` : "";
    audioPlayer.load();
}

/* =========================
   LANGUE
   ========================= */

function changeLanguage(lang) {
    currentLanguage = lang;
    loadLegend(currentLanguage, currentLegendKey);
}

/* =========================
   FILTRE PAYS
   ========================= */

function filterCountry(country) {
    const section = document.querySelector(".legende");
    if (country === "all" || section.dataset.country === country) {
        section.style.display = "block";
    } else {
        section.style.display = "none";
    }
}

/* =========================
   INITIALISATION
   ========================= */

document.addEventListener("DOMContentLoaded", () => {
    loadLegend(currentLanguage, currentLegendKey);
});
