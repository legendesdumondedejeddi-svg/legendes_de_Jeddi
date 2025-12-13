function readLegend(button) {
    const text = button
        .parentElement
        .querySelector(".legend-text")
        .innerText;

    const lang = document.documentElement.lang || "fr-FR";

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;

    speechSynthesis.cancel(); // stop si déjà en cours
    speechSynthesis.speak(utterance);
}
