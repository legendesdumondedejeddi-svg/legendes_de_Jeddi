/* =========================
   CHARGEMENT D’UNE LÉGENDE
   ========================= */

async function loadLegend(key) {
    try {
        const response = await fetch(`translations/fr/${key}.json`);

        if (!response.ok) {
            throw new Error("Fichier JSON introuvable");
        }

        const legend = await response.json();

        // Titre
        document.getElementById("lang-title").textContent = legend.title || "";

        // Sous-titre
        document.getElementById("lang-subtitle").textContent = legend.subtitle || "";

        // Texte (respect des retours à la ligne)
        document.getElementById("lang-text").innerHTML =
            legend.text
                .split("\n")
                .map(p => `<p>${p}</p>`)
                .join("");

        // Audio
        const audio = document.getElementById("audio-player");
        audio.src = `audio/${legend.audio}`;
        audio.load();

    } catch (error) {
        console.error("Erreur chargement légende :", error);
        document.getElementById("lang-text").innerHTML =
            "<p>Impossible de charger la légende.</p>";
    }
}

/* =========================
   FILTRE PAR PAYS (OPTIONNEL)
   ========================= */

function filterCountry(country) {
    const section = document.querySelector(".legende");

    if (!section) return;

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
    // ⚠️ NOM DU FICHIER SANS .json
    loadLegend("aubepin");
});
