// Sélection des liens de langues
const langLinks = document.querySelectorAll(".submenu a");

// Container pour injecter les légendes
const legendeContainer = document.getElementById("legendes-list");

// Lecteur audio
const audioPlayer = document.getElementById("audio-player");

// Fonction principale pour changer de langue
langLinks.forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        const lang = link.dataset.lang;

        // Chargement du fichier JSON correspondant à la langue
        fetch(`translations/${lang}.json`)
            .then(res => res.json())
            .then(data => {
                // Changer le texte des titres et intro
                document.getElementById("title-welcome")?.textContent = data.title_welcome;
                document.getElementById("intro-text")?.textContent = data.intro_text;
                document.getElementById("legendes-title")?.textContent = data.legendes_title;

                // Vider le container des légendes
                legendeContainer.innerHTML = "";

                // Ajouter les légendes
                data.legendes.forEach(legende => {
                    const div = document.createElement("div");
                    div.className = "legende";
                    div.innerHTML = `
                        <h2>${legende.title}</h2>
                        <p>${legende.text}</p>
                        <button onclick="playAudio('${legende.audio}')">▶ Écouter</button>
                    `;
                    legendeContainer.appendChild(div);
                });
            })
            .catch(err => console.error("Erreur chargement JSON:", err));
    });
});

// Fonction pour lire l'audio d'une légende
function playAudio(src) {
    audioPlayer.src = src;
    audioPlayer.play();
    // Idée : ajouter une animation ou changer l'icône du bouton pendant la lecture
}
