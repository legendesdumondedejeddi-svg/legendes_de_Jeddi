document.addEventListener("DOMContentLoaded", function () {
    console.log("JS chargé.");

    var main = document.querySelector("main");
    if (main) {
        main.style.opacity = 0;
        main.style.transition = "opacity 0.8s ease";
        setTimeout(() => main.style.opacity = 1, 50);
    }

    var btn = document.createElement("button");
    btn.textContent = "↑";
    btn.style.position = "fixed";
    btn.style.bottom = "20px";
    btn.style.right = "20px";
    btn.style.padding = "10px";
    btn.style.zIndex = 999;
    btn.style.display = "none";
    document.body.appendChild(btn);

    window.addEventListener("scroll", () => {
        btn.style.display = window.scrollY > 300 ? "block" : "none";
    });

    btn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});
document.addEventListener("DOMContentLoaded", () => {
    const bouton = document.getElementById("lireLegende");
    const texte = document.getElementById("texteLegende");

    if (bouton && texte) {
        bouton.addEventListener("click", () => {
            const utterance = new SpeechSynthesisUtterance(texte.innerText);
            utterance.lang = "fr-FR";
            utterance.rate = 1.0;    // vitesse
            utterance.pitch = 1.0;   // hauteur
            speechSynthesis.cancel();
            speechSynthesis.speak(utterance);
        });
    }
});
