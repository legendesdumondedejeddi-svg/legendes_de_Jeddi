document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("night-toggle");
    const body = document.body;

    btn.addEventListener("click", () => {
        if (body.classList.contains("nuit")) {
            body.classList.remove("nuit");
            body.classList.add("jour");
        } else {
            body.classList.remove("jour");
            body.classList.add("nuit");
        }
    });
});
