const langLinks = document.querySelectorAll(".submenu a");
const legendeContainer = document.getElementById("legendes-list");
const audioPlayer = document.getElementById("audio-player");

langLinks.forEach(link => {
    link.addEventListener("click", e => {
        e.preventDefault();
        const lang = link.dataset.lang;
        fetch(`translations/${lang}.json`)
            .then(res => res.json())
            .then(data => {
                document.getElementById("title-welcome")?.textContent = data.title_welcome;
                document.getElementById("intro-text")?.textContent = data.intro_text;
                document.getElementById("legendes-title")?.textContent = data.legendes_title;
                legendeContainer.innerHTML = "";
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
            });
    });
});

function playAudio(src) {
    audioPlayer.src = src;
    audioPlayer.play();
}
