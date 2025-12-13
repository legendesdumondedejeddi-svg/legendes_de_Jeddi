function lire(bouton) {
    const texte = bouton.previousElementSibling.innerText;
    const voix = new SpeechSynthesisUtterance(texte);
    voix.lang = "fr-FR";
    speechSynthesis.cancel();
    speechSynthesis.speak(voix);
}
