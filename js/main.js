// main.js

// Changer la langue du menu et des textes
function changeLanguage(lang) {
    fetch("translations/" + lang + ".json")
        .then(response => response.json())
        .then(data => {
            // Menu
            document.querySelector('a[href="index.html"]').textContent = data.menu.accueil;
            document.querySelector('a[href="legendes.html"]').textContent = data.menu.legendes;
            document.querySelector('a[href="apropos.html"]').textContent = data.menu.apropos;
            document.querySelector('a[href="don.html"]').textContent = data.menu.don;
            document.querySelector('.lang-switch span').textContent = data.menu.langue + " ▾";

            // Page À propos
            const aproposTitle = document.querySelector('#apropos-title');
            const aproposText = document.querySelector('#apropos-text');
            if (aproposTitle && aproposText) {
                aproposTitle.textContent = data.apropos.title;
                aproposText.textContent = data.apropos.texte;
            }

            // Page DON
            const donTitle = document.querySelector('#don-title');
            const donText = document.querySelector('#don-text');
            if (donTitle && donText) {
                donTitle.textContent = data.don.title;
                donText.textContent = data.don.texte;
            }
        });
}

// Changer l’audio dans legendes.html
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
