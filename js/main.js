function changeAudio(lang) {
    const audio = document.getElementById("audio-player");
    audio.src = "audio/aubepin_" + lang + ".mp3";
    audio.load();
    audio.play();
}

function changeLang(lang) {
    fetch("translations/" + lang + ".json")
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("[data-i18n]").forEach(el => {
                const key = el.getAttribute("data-i18n");
                if (data[key]) el.innerText = data[key];
            });
        });
}
