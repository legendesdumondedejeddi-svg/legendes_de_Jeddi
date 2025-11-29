// simple helper: cancel speech on navigation
window.addEventListener("beforeunload", function(){ try{ window.speechSynthesis.cancel() }catch(e){} });
console.log("Script chargé.");
