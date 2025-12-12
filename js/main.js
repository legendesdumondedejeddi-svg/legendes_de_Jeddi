let currentLang = "fr";
let translations = {};

async function setLanguage(lang) {
    currentLang = lang;

    const response = await fetch(`translations/${lang}.json`);
    translations = await response.json();

    translatePage();
}

function translatePage() {
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[key]) {
            el.textContent = translations[key];
        }
    });
}

setLanguage("fr");

