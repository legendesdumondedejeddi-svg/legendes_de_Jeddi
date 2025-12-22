document.addEventListener("DOMContentLoaded", () => {

  // 1. Charger la légende
  fetch("legends/aubepin.json")
    .then(response => {
      if (!response.ok) {
        throw new Error("JSON introuvable");
      }
      return response.json();
    })
    .then(data => {

      // 2. Titre et sous-titre
      document.getElementById("legend-title").textContent = data.title;
      document.getElementById("legend-subtitle").textContent = data.subtitle;

      // 3. Texte (gestion automatique des paragraphes)
      document.getElementById("legend-text").innerHTML =
        data.text.replace(/\n\n/g, "<br><br>");

      // 4. Audio (si présent)
      if (data.audio) {
        const audio = document.getElementById("audio-player");
        audio.src = "audio/" + data.audio;
        audio.style.display = "block";
      }
    })
    .catch(error => {
      console.error("Erreur :", error);
    });

});
