let currentLang = 'fr';
let translations = {};

function loadTranslation(lang) {
    currentLang = lang;
    fetch(`translations/${lang}.json`)
    .then(resp => resp.json())
    .then(data => {
        translations = data;
        updateTexts();
    });
}

function updateTexts() {
    document.querySelectorAll('[data-key]').forEach(el => {
        const keys = el.dataset.key.split('.');
        let text = translations;
        keys.forEach(k => {
            if(text) text = text[k];
        });
        if(text) el.innerText = text;
    });
}

// changer de langue via menu
document.querySelectorAll('.submenu a[data-lang]').forEach(a => {
    a.addEventListener('click', e => {
        e.preventDefault();
        loadTranslation(a.dataset.lang);
    });
});

// audio multilingue
function lire(bouton) {
    const texte = bouton.previousElementSibling.innerText;
    const voix = new SpeechSynthesisUtterance(texte);
    switch(currentLang) {
        case 'fr': voix.lang = 'fr-FR'; break;
        case 'en': voix.lang = 'en-US'; break;
        case 'de': voix.lang = 'de-DE'; break;
        case 'es': voix.lang = 'es-ES'; break;
        case 'it': voix.lang = 'it-IT'; break;
        default: voix.lang = 'fr-FR';
    }
    speechSynthesis.cancel();
    speechSynthesis.speak(voix);
}
