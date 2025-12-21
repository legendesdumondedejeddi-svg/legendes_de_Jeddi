document.addEventListener("DOMContentLoaded", () => {

  fetch("legends/Aubepin.json")
    .then(response => response.json())
    .then(data => {
      document.getElementById("legend-title").textContent = data.title;
      document.getElementById("legend-subtitle").textContent = data.subtitle;
      document.getElementById("legend-text").innerHTML = data.text;
    })
    .catch(error => {
      console.error("Erreur de chargement de la légende :", error);
    });

});
