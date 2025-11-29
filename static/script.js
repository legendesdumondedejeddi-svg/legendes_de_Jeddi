// script.js
console.log("Script loaded.");

// Simple TTS using Web Speech API (client side)
function ttsRead() {
    try {
        const article = document.querySelector('.legende-contenu');
        if (!article) return alert("Aucune légende à lire.");
        // get text content without HTML tags
        const text = article.innerText || article.textContent;
        if (!window.speechSynthesis) return alert("TTS non supporté par ce navigateur.");
        const utter = new SpeechSynthesisUtterance(text);
        // prefer a french voice if available
        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length) {
            const fr = voices.find(v => v.lang && v.lang.startsWith('fr'));
            if (fr) utter.voice = fr;
        }
        utter.rate = 0.95;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
    } catch (e) {
        console.error(e);
        alert("Impossible de lancer la lecture vocale.");
    }
}
