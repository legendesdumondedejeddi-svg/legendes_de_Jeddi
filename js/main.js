function loadLanguage(lang) {
    fetch(`translations/${lang}.json`)
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("[data-i18n]").forEach(el => {
                const key = el.getAttribute("data-i18n");
                if (data[key]) {
                    el.textContent = data[key];
                }
            });
        });
}

document.querySelectorAll(".submenu a").forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        loadLanguage(link.textContent.toLowerCase());
    });
});

// langue par défaut
loadLanguage("fr");
