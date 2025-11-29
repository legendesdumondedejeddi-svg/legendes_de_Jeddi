// script.js - comportements simples et robustes pour débutant
document.addEventListener("DOMContentLoaded", function() {
  // Toggle mobile/compact menu (si tu ajoutes un bouton #menu-toggle)
  var btn = document.getElementById("menu-toggle");
  if (btn) {
    btn.addEventListener("click", function(e){
      var nav = document.getElementById("main-nav");
      if (nav) nav.classList.toggle("open");
    });
  }

  // dropdown accessible : ouvre/ferme au clic, ferme si clic en dehors
  document.querySelectorAll(".drop > a").forEach(function(link){
    link.addEventListener("click", function(e){
      e.preventDefault();
      var parent = link.parentElement;
      parent.classList.toggle("open");
    });
  });

  document.addEventListener("click", function(e){
    document.querySelectorAll(".drop").forEach(function(d){
      if (!d.contains(e.target)) d.classList.remove("open");
    });
  });

  // simple client-side form validation for grimoire
  var grimoireForm = document.querySelector("form#grimoire-form");
  if (grimoireForm){
    grimoireForm.addEventListener("submit", function(e){
      var t = grimoireForm.querySelector("[name='title']");
      var c = grimoireForm.querySelector("[name='content']");
      if (!t.value.trim() || !c.value.trim()){
        e.preventDefault();
        alert("Veuillez remplir le titre et le contenu.");
      }
    });
  }
});
