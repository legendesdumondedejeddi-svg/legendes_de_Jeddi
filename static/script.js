// script.js - effets légers (licorne run handled in CSS), small helpers
console.log("JS enchanté chargé.");

// Small: stop TTS if user navigates away
window.addEventListener("beforeunload", function(){
    if (window.speechSynthesis) window.speechSynthesis.cancel();
});
