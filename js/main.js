document.addEventListener("DOMContentLoaded", () => {

  fetch("legends/aubepin_la_fille_femme.json")
    .then(response => response.json())
    .then(data => {
      document.getElementById("legend-title").textContent = data.title;
      document.getElementById("legend-subtitle").textContent = data.subtitle;
     document.getElementById("legend-text").innerHTML =
  data.text.replace(/\n\n/g, "<br><br>");
    })
    .catch(error => {
      console.error("Erreur de chargement de la légende :", error);
    });

});
