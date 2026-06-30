function copyCA() {
    const ca = "GEEQMeTNRYvQKBHZo2jEaHd7j93AZugmSa6UsktJpump";
    navigator.clipboard.writeText(ca);
    alert("Contract Address Copied!");
}

// Fade-in animation
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add("show");
        }
    });
}, {
    threshold: 0.15
});

document.querySelectorAll("section, .card").forEach((el) => {
    el.classList.add("hidden");
    observer.observe(el);
});

// Floating background
const bg = document.createElement("div");
bg.className = "floating-bg";
document.body.prepend(bg);

const emojis = ["🍞","🐾"];

for(let i=0;i<16;i++){

    const e=document.createElement("div");

    e.className="float";

    e.innerHTML=emojis[Math.floor(Math.random()*emojis.length)];

    e.style.left=Math.random()*100+"vw";

    e.style.animationDuration=(18+Math.random()*12)+"s";

    e.style.animationDelay=(-Math.random()*30)+"s";

    e.style.fontSize=(18+Math.random()*18)+"px";

    bg.appendChild(e);

}
