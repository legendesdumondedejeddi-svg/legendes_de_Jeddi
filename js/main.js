// Chargement des traductions
let translations = {};

// Charger un fichier de langue
function loadLanguage(lang) {
    fetch("translations/" + lang + ".json")
        .then(response => {
            if (!response.ok) {
                throw new Error("Fichier langue introuvable");
            }
            return response.json();
        })
        .then(data => {
            translations = data;
            applyLanguage();
        })
        .catch(error => {
            console.error("Erreur de traduction :", error);
        });
}

// Appliquer la langue au texte
function applyLanguage() {
    document.getElementById("lang-title").innerText = translations.title;
    document.getElementById("lang-subtitle").innerText = translations.subtitle;
    document.getElementById("lang-text").innerHTML = "<strong>" + translations.text + "</strong>";
}

// Changer la langue (texte + audio)
function changeLanguage(lang) {
    loadLanguage(lang);
    changeAudio(lang);
}

// Changer l'audio
function changeAudio(lang) {
    const audio = document.getElementById("audio-player");

    if (!audio) {
        alert("Lecteur audio introuvable.");
        return;
    }

    audio.src = "audio/aubepin_" + lang + ".mp3";
    audio.load();
    audio.play();
}

// Langue par défaut au chargement
document.addEventListener("DOMContentLoaded", function () {
    loadLanguage("fr");
});
