document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".menu-toggle");
    const navbar = document.querySelector(".navbar");
    if (toggle && navbar) {
        toggle.addEventListener("click", () => {
            navbar.classList.toggle("open");
        });
    }
    const topBtn = document.createElement("button");
    topBtn.textContent = "↑";
    topBtn.id = "topButton";
    document.body.appendChild(topBtn);
    topBtn.style.position = "fixed";
    topBtn.style.bottom = "25px";
    topBtn.style.right = "25px";
    topBtn.style.padding = "10px 15px";
    topBtn.style.border = "2px solid #3d2b1f";
    topBtn.style.background = "#f2dfc2";
    topBtn.style.cursor = "pointer";
    topBtn.style.fontSize = "20px";
    topBtn.style.display = "none";
    topBtn.style.borderRadius = "6px";
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            topBtn.style.display = "block";
        } else {
            topBtn.style.display = "none";
        }
    });
    topBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
    const main = document.querySelector("main");
    if (main) {
        main.style.opacity = 0;
        main.style.transition = "opacity 1s ease";
        setTimeout(() => { main.style.opacity = 1; }, 50);
    }
});
