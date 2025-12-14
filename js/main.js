/* =====================================================
   MAIN.JS — LÉGENDES DU MONDE DE JEDDI
   Gestion :
   - Lecture audio des légendes
   - Traductions automatiques
   - Filtrage des légendes par pays
   ===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================
       1. GESTION DE LA LANGUE
       ===================================== */

    let currentLang = "fr";

    function loadTranslations(lang) {
        fetch(`translations/${lang}.json`)
            .then(response => response.json())
            .then(translations => {
                document.querySelectorAll("[data-i18n]").forEach(element => {
                    const key = element.getAttribute("data-i18n");
                    if (translations[key]) {
                        element.textContent = translations[key];
                    }
                });
            })
            .catch(error => {
                console.error("Erreur de traduction :", error);
            });
    }

    // Chargement initial en français
    loadTranslations(currentLang);

    // Changement de langue via le menu
    document.querySelectorAll(".lang-switch a").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            const lang = link.getAttribute("data-lang");
            if (lang) {
                currentLang = lang;
                loadTranslations(lang);
            }
        });
    });

    /* =====================================
       2. LECTURE AUDIO DES LÉGENDES
       ===================================== */

    const audioButtons = document.querySelectorAll(".play-audio");

    audioButtons.forEach(button => {
        button.addEventListener("click", () => {

            const audioSrc = button.getAttribute("data-audio");
            const audioElement = button.nextElementSibling;

            // Arrêter tous les autres audios
            document.querySelectorAll(".audio-player").forEach(audio => {
                if (audio !== audioElement) {
                    audio.pause();
                    audio.currentTime = 0;
                }
            });

            // Lancer l'audio demandé
            audioElement.src = audioSrc;
            audioElement.play();
        });
    });

    /* =====================================
       3. FILTRAGE DES LÉGENDES PAR PAYS
       ===================================== */

    document.querySelectorAll("[data-filter]").forEach(filterButton => {
        filterButton.addEventListener("click", event => {
            event.preventDefault();
            const country = filterButton.getAttribute("data-filter");

            document.querySelectorAll(".legende").forEach(legende => {
                if (country === "Tous" || legende.dataset.pays === country) {
                    legende.style.display = "block";
                } else {
                    legende.style.display = "none";
                }
            });
        });
    });

});
