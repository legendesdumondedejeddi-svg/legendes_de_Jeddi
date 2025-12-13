async function loadLanguage(lang) {
    const response = await fetch(`translations/${lang}.json`);
    const translations = await response.json();

    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[key]) {
            el.innerText = translations[key];
        }
    });
}

document.querySelectorAll(".submenu a").forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        const lang = link.innerText.toLowerCase();
        loadLanguage(lang);
    });
});

// langue par défaut
loadLanguage("fr");
