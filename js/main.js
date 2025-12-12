let currentLang = localStorage.getItem("lang") || "fr";

function changeLang(lang) {
    currentLang = lang;
    localStorage.setItem("lang", lang);
    loadTranslations();
}

function loadTranslations() {
    fetch(`translations/${currentLang}.json`)
        .then(r => r.json())
        .then(data => {
            document.querySelectorAll("[data-i18n]").forEach(el => {
                let key = el.getAttribute("data-i18n");
                if (data[key]) el.innerHTML = data[key];
            });
        });
}

loadTranslations();
