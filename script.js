/* ==========================================================
   CatLoaf AI Bakery
   script.js
   Part 1
========================================================== */

"use strict";

/* ==========================================================
   Helpers
========================================================== */

const $ = (selector) => document.querySelector(selector);

const $$ = (selector) => document.querySelectorAll(selector);

/* ==========================================================
   Copy Contract
========================================================== */

function copyCA(){

    const address = $("#ca").innerText.trim();

    navigator.clipboard.writeText(address);

    const btn = document.querySelector("button");

    const old = btn.innerHTML;

    btn.innerHTML = "✅ Copied";

    setTimeout(()=>{

        btn.innerHTML = old;

    },1800);

}

/* ==========================================================
   Counter Animation
========================================================== */

function animateValue(element,start,end,duration){

    let startTime = null;

    function step(timestamp){

        if(!startTime)
            startTime = timestamp;

        const progress = Math.min(

            (timestamp-startTime)/duration,

            1

        );

        element.textContent = Math.floor(

            progress*(end-start)+start

        );

        if(progress<1){

            requestAnimationFrame(step);

        }

    }

    requestAnimationFrame(step);

}

/* ==========================================================
   Run Counters
========================================================== */

function runCounters(){

    document.querySelectorAll("[data-count]")

    .forEach(el=>{

        animateValue(

            el,

            0,

            Number(el.dataset.count),

            1400

        );

    });

}

/* ==========================================================
   Progress Bars
========================================================== */

function animateProgress(){

    document.querySelectorAll(

        ".progress span"

    ).forEach(bar=>{

        const width = bar.dataset.width || "0";

        bar.style.width="0%";

        setTimeout(()=>{

            bar.style.transition="width 1.6s ease";

            bar.style.width=width+"%";

        },350);

    });

}

/* ==========================================================
   Live Timer
========================================================== */

function bakeryClock(){

    const target = $("#bakery-time");

    if(!target)
        return;

    function tick(){

        const now = new Date();

        target.innerHTML=

            now.toLocaleTimeString();

    }

    tick();

    setInterval(tick,1000);

}

/* ==========================================================
   Last Updated
========================================================== */

let lastUpdate = new Date();

function updateLastSeen(){

    const el=$("#last-update");

    if(!el)
        return;

    function refresh(){

        const diff=Math.floor(

            (Date.now()-lastUpdate)/1000

        );

        el.innerHTML=

            diff+" sec ago";

    }

    refresh();

    setInterval(refresh,1000);

}

/* ==========================================================
   Fade In
========================================================== */

function reveal(){

    document.body.classList.add(

        "loaded"

    );

}

/* ==========================================================
   Startup
========================================================== */

window.addEventListener(

    "DOMContentLoaded",

    ()=>{

        reveal();

        bakeryClock();

        updateLastSeen();

        runCounters();

        animateProgress();

    }

);