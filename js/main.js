// main.js

// Liste des langues disponibles
const LANGUAGES = ["fr", "en", "de", "es", "it"];
let currentLang = "fr"; // langue par défaut

// Fonction pour charger un fichier JSON de traductions
async function loadTranslations(lang) {
    try {
        const response = await fetch(`translations/${lang}.json`);
        if (!response.ok) throw new Error("Fichier de traduction introuvable");
        const data = await response.json();
        return data;
    } catch (err) {
        console.error("Erreur de chargement des traductions :", err);
        return {};
    }
}

// Fonction pour mettre à jour toutes les légendes
async function updateLegends(lang) {
    const translations = await loadTranslations(lang);
    const legendElements = document.querySelectorAll(".legend");
    legendElements.forEach((el) => {
        const id = el.id; // identifiant de la légende
        if (translations[id]) {
            el.querySelector(".legend-title").textContent = translations[id].title;
            el.querySelector(".legend-text").textContent = translations[id].text;

            // Mettre à jour la source audio
            const audioEl = el.querySelector("audio source");
            if (audioEl) {
                audioEl.src = `static/audio/${id}_${lang}.mp3`;
                audioEl.parentElement.load(); // recharge l'audio
            }
        }
    });
}

// Gestion du menu déroulant langues
const langLinks = document.querySelectorAll(".lang-switch a");
langLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        const selectedLang = link.getAttribute("data-lang");
        if (LANGUAGES.includes(selectedLang)) {
            currentLang = selectedLang;
            updateLegends(currentLang);
        }
    });
});

// Initialisation au chargement
document.addEventListener("DOMContentLoaded", () => {
    updateLegends(currentLang);
});
