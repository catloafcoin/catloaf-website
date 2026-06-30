function copyCA() {
    const ca = "GEEQMeTNRYvQKBHZo2jEaHd7j93AZugmSa6UsktJpump";

    navigator.clipboard.writeText(ca).then(() => {
        alert("✅ Contract Address copied!");
    }).catch(() => {
        alert("Copy failed. Please copy it manually.");
    });
}

const cards = document.querySelectorAll(".card");

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
        }
    });
}, {
    threshold: 0.2
});

cards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(40px)";
    card.style.transition = "all 0.8s ease";
    observer.observe(card);
});