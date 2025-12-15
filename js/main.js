function changeAudio(lang) {
    const audio = document.getElementById("audio-player");

    if (!audio) {
        alert("Lecteur audio introuvable.");
        return;
    }

    audio.src = "audio/aubepin_" + lang + ".mp3";
    audio.load();
    audio.play();
}
