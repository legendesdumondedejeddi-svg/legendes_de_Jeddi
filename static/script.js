// static/script.js

// Lecture vocale (TTS) : bouton dans templates si présent
function speakText(text) {
    if (!("speechSynthesis" in window)) {
        alert("TTS non supporté dans ce navigateur.");
        return;
    }
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 0.95;
    utter.pitch = 1;
    speechSynthesis.cancel();
    speechSynthesis.speak(utter);
}

// Ajoute comportement aux boutons .btn-lecture s'ils existent
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector(".btn-lecture");
    if (btn) {
        btn.addEventListener("click", function () {
            const contentEl = document.querySelector(".legende-contenu");
            if (contentEl) speakText(contentEl.innerText.trim());
        });
    }
});
