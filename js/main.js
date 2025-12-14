function loadLanguage(lang) {
    fetch(`translations/${lang}.json`)
        .then(res => res.json())
        .then(data => {
           document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".play-audio");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const audioSrc = button.getAttribute("data-audio");
            const audio = button.nextElementSibling;

            // Stop tous les autres audios
            document.querySelectorAll(".audio-player").forEach(a => {
                if (a !== audio) {
                    a.pause();
                    a.currentTime = 0;
                }
            });

            audio.src = audioSrc;
            audio.play();
        });
    });
});

document.querySelectorAll(".submenu a").forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        loadLanguage(link.textContent.toLowerCase());
    });
});

// langue par défaut
loadLanguage("fr");
