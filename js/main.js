document.addEventListener("DOMContentLoaded", () => {
  fetch("legends/aubepin.json")
    .then(res => res.json())
    .then(data => {
      document.getElementById("legend-title").textContent = data.title;
      document.getElementById("legend-subtitle").textContent = data.subtitle;

      document.getElementById("legend-text").innerHTML =
        data.text.replace(/\n\n/g, "<p></p>");

      const audio = document.getElementById("audio-player");
      audio.src = "audio/" + data.audio;
    })
    .catch(err => console.error("Erreur légende :", err));
});
