let currentLanguage = "fr";
let currentLegendKey = "aubepin"; // légende affichée par défaut
let translationsData = {};

/* =========================
   CHARGEMENT DES TRADUCTIONS
   ========================= */
async function loadTranslations(lang) {
    try {
        const response = await fetch(`translations/${lang}.json`);
        if (!response.ok) throw new Error("Fichier de traduction introuvable");
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
        document.getElementById("lang-title").textContent = "";
        document.getElementById("lang-subtitle").textContent = "";
        document.getElementById("lang-text").innerHTML = "<p>Contenu indisponible</p>";
        document.getElementById("audio-player").src = "";
        return;
    }

    const legend = translationsData[key];

    document.getElementById("lang-title").textContent = legend.title || "";
    document.getElementById("lang-subtitle").textContent = legend.subtitle || "";

    const textContainer = document.getElementById("lang-text");
    textContainer.innerHTML = legend.text
        .split("\n")
        .map(p => `<p>${p.trim()}</p>`)
        .join("");

    const audioPlayer = document.getElementById("audio-player");
    if (legend.audio) {
        audioPlayer.src = `audio/${legend.audio}`;
        audioPlayer.load();
    } else {
        audioPlayer.src = "";
    }
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
