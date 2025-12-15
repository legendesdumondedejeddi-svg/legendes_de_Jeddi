let currentLanguage = "fr";
let currentLegendKey = "aubepin"; // légende affichée par défaut
let translationsData = {};

/* =========================
   CHARGEMENT DES TRADUCTIONS
   ========================= */

async function loadTranslations(lang) {
    try {
        const response = await fetch(`translations/${lang}.json`);
        translationsData = await response.json();
        currentLanguage = lang;
        displayLegend(currentLegendKey);
    } catch (error) {
        console.error("Erreur de chargement des traductions :", error);
    }
}

/* =========================
   AFFICHAGE DE LA LÉGENDE
   ========================= */

function displayLegend(key) {
    if (!translationsData[key]) {
        console.warn("Légende introuvable :", key);
        return;
    }

    const legend = translationsData[key];

    document.getElementById("lang-title").textContent = legend.title;
    document.getElementById("lang-subtitle").textContent = legend.subtitle;

    // Respect de la mise en page originale
    const textContainer = document.getElementById("lang-text");
    textContainer.innerHTML = legend.text
        .split("\n")
        .map(p => `<p>${p}</p>`)
        .join("");

    // Audio
    const audioPlayer = document.getElementById("audio-player");
    audioPlayer.src = `audio/${legend.audio}`;
    audioPlayer.load();
}

/* =========================
   CHANGEMENT DE LANGUE
   ========================= */

function changeLanguage(lang) {
    loadTranslations(lang);
}

/* =========================
   FILTRE PAR PAYS
   ========================= */

function filterCountry(country) {
    const sections = document.querySelectorAll(".legende");

    sections.forEach(section => {
        if (section.dataset.country === country || country === "all") {
            section.style.display = "block";
        } else {
            section.style.display = "none";
        }
    });
}

/* =========================
   INITIALISATION
   ========================= */

document.addEventListener("DOMContentLoaded", () => {
    loadTranslations(currentLanguage);
});
