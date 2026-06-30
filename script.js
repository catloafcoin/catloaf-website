function copyCA() {
    const ca = document.getElementById("ca").innerText;
    navigator.clipboard.writeText(ca);
    alert("Contract Address Copied!");
}

// Fade in sections
const observer = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }
    });
},{
    threshold:0.15
});

document.querySelectorAll("section,.card").forEach(el=>{
    el.classList.add("hidden");
    observer.observe(el);
});

// Floating bread & paws
const bg=document.createElement("div");
bg.className="floating-bg";
document.body.prepend(bg);

const icons=["🍞","🐾"];

for(let i=0;i<20;i++){

    const item=document.createElement("div");

    item.className="float";

    item.innerHTML=icons[Math.floor(Math.random()*icons.length)];

    item.style.left=Math.random()*100+"vw";

    item.style.animationDuration=(18+Math.random()*15)+"s";

    item.style.animationDelay=(-Math.random()*40)+"s";

    item.style.fontSize=(18+Math.random()*22)+"px";

    bg.appendChild(item);

}
