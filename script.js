/* ==========================================================
   CatLoaf AI Bakery
   script.js
   Part 1
   Core Engine
========================================================== */

"use strict";

/* ==========================================================
   Bakery App
========================================================== */

const Bakery = {

    version: "1.0",

    refreshSeconds: 300,

    scannerData: [],

    lastUpdated: null,

    init() {

        console.log("🍞 CatLoaf AI Bakery Initializing...");

        this.cacheDOM();

        this.startClock();

        this.animateCounters();

        this.observeSections();

        this.startRefreshTimer();

        this.loadScanner();

    },

    /* ======================================================
       Cache Elements
    ====================================================== */

    cacheDOM() {

        this.scanner =
            document.getElementById("scanner-container");

        this.lastUpdate =
            document.getElementById("last-update");

        this.clock =
            document.getElementById("bakery-time");

    },

    /* ======================================================
       Clock
    ====================================================== */

    startClock() {

        const update = () => {

            const now = new Date();

            if(this.clock){

                this.clock.textContent =
                    now.toLocaleTimeString();

            }

        };

        update();

        setInterval(update,1000);

    },

    /* ======================================================
       Animated Counters
    ====================================================== */

    animateCounters(){

        const counters =
            document.querySelectorAll("[data-count]");

        counters.forEach(counter=>{

            const target =
                Number(counter.dataset.count);

            let value = 0;

            const step =
                Math.max(1,target/40);

            const timer = setInterval(()=>{

                value += step;

                if(value >= target){

                    value = target;

                    clearInterval(timer);

                }

                counter.textContent =
                    Math.floor(value);

            },25);

        });

    },

    /* ======================================================
       Scroll Reveal
    ====================================================== */

    observeSections(){

        const observer =
            new IntersectionObserver(entries=>{

                entries.forEach(entry=>{

                    if(entry.isIntersecting){

                        entry.target.classList.add("show");

                    }

                });

            },{

                threshold:.12

            });

        document
            .querySelectorAll(".card,.status-item")
            .forEach(el=>{

                el.classList.add("fade-in");

                observer.observe(el);

            });

    },

    /* ======================================================
       Refresh Timer
    ====================================================== */

    startRefreshTimer(){

        let seconds = 0;

        setInterval(()=>{

            seconds++;

            if(this.lastUpdate){

                this.lastUpdate.textContent =
                    `${seconds}s ago`;

            }

        },1000);

    },

    /* ======================================================
       Scanner Loader
    ====================================================== */

    loadScanner(){

        if(!this.scanner){

            return;

        }

        this.scanner.innerHTML = `

        <div class="scanner-loading">

            <div class="loading-loaf">

                🍞

            </div>

            <h3>

                AI Bakery is scanning fresh launches...

            </h3>

            <p>

                Looking for today's hottest Pump.fun projects.

            </p>

        </div>

        `;

        /*
            Part 2
            will replace this
            with dynamic data.
        */

    }

};

/* ==========================================================
   Launch Bakery
========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>Bakery.init()

);
/* ======================================================
   Scanner Engine
====================================================== */

renderScanner(coins){

    if(!this.scanner) return;

    this.scanner.innerHTML = "";

    coins.forEach((coin,index)=>{

        const card = document.createElement("div");

        card.className = "coin-card";

        card.innerHTML = `

        <div class="coin-rank">
            🥇 #${index+1}
        </div>

        <div class="coin-header">

            <img
                class="coin-logo"
                src="${coin.logo}"
                alt="${coin.name}"
            >

            <div class="coin-info">

                <div class="coin-name">
                    ${coin.name}
                </div>

                <div class="coin-symbol">
                    ${coin.symbol}
                </div>

            </div>

        </div>

        <div class="coin-price">

            ${coin.change24h}%

        </div>

        <div class="coin-change gain">

            ${coin.status}

        </div>

        <div class="coin-stats">

            <div class="stat">

                <small>Volume</small>

                <strong>${coin.volume}</strong>

            </div>

            <div class="stat">

                <small>Market Cap</small>

                <strong>${coin.marketCap}</strong>

            </div>

            <div class="stat">

                <small>Age</small>

                <strong>${coin.age}</strong>

            </div>

            <div class="stat">

                <small>Holders</small>

                <strong>${coin.holders}</strong>

            </div>

        </div>

        <div class="loaf-title">

            <span>

                🍞 Loaf Score

            </span>

            <span>

                ${coin.score}/100

            </span>

        </div>

        <div class="loaf-bar">

            <div
                class="loaf-fill"
                style="width:${coin.score}%"
            ></div>

        </div>

        <div class="sparkline">

            ${this.generateSparkline()}

        </div>

        <div class="coin-footer">

            <span class="updated">

                Updated just now

            </span>

            <a
                class="view-btn"
                href="${coin.url}"
                target="_blank"
            >

                View →

            </a>

        </div>

        `;

        this.scanner.appendChild(card);

    });

},

/* ======================================================
   Sparkline Generator
====================================================== */

generateSparkline(){

    let html="";

    for(let i=0;i<12;i++){

        const height =
            Math.floor(
                Math.random()*70
            )+25;

        html+=`

        <span
            class="spark"
            style="height:${height}%"
        ></span>

        `;

    }

    return html;

},

/* ======================================================
   Temporary Scanner Data
====================================================== */

loadScanner(){

    const coins=[

        {

            name:"Loading",

            symbol:"$WAIT",

            logo:"assets/logo.jpg",

            change24h:"+0",

            volume:"--",

            marketCap:"--",

            holders:"--",

            age:"--",

            score:0,

            status:"Scanning...",

            url:"#"

        }

    ];

    this.renderScanner(coins);

},
/* ======================================================
   Data Service
====================================================== */

async fetchScannerData(){

    try{

        console.log("🍞 Fetching scanner data...");

        const response = await fetch(

            "scanner.json?ts=" + Date.now(),

            {

                cache:"no-store"

            }

        );

        if(!response.ok){

            throw new Error("Unable to load scanner.json");

        }

        const data = await response.json();

        this.scannerData = data;

        this.lastUpdated = new Date();

        this.renderScanner(data);

        this.updateHeroStats(data);

        console.log("✅ Scanner Updated");

    }

    catch(error){

        console.error(error);

        this.showScannerError();

    }

},

/* ======================================================
   Scanner Refresh
====================================================== */

startScannerRefresh(){

    this.fetchScannerData();

    setInterval(()=>{

        this.fetchScannerData();

    },this.refreshSeconds*1000);

},

/* ======================================================
   Update Hero
====================================================== */

updateHeroStats(data){

    const scannerCount =

        document.querySelector("#scanner-count");

    if(scannerCount){

        scannerCount.textContent = data.length;

    }

    const last =

        document.getElementById("last-update");

    if(last){

        last.textContent="Just now";

    }

},

/* ======================================================
   Scanner Error
====================================================== */

showScannerError(){

    if(!this.scanner) return;

    this.scanner.innerHTML=`

        <div class="scanner-empty">

            <h3>

                ⚠ Scanner Offline

            </h3>

            <p>

                The Bakery couldn't retrieve today's fresh launches.

                We'll automatically try again shortly.

            </p>

        </div>

    `;

},
/* ======================================================
   AI Bakery Engine
====================================================== */

processScannerData(data){

    if(!Array.isArray(data)){

        return [];

    }

    return data

        .filter(coin=>{

            return coin.name &&
                   coin.symbol;

        })

        .map(coin=>{

            coin.score =

                this.calculateLoafScore(coin);

            return coin;

        })

        .sort(

            (a,b)=>b.score-a.score

        )

        .slice(0,5);

},

/* ======================================================
   Loaf Score
====================================================== */

calculateLoafScore(coin){

    let score = 0;

    const gain =

        Number(

            String(coin.change24h)

            .replace("%","")

            .replace("+","")

        ) || 0;

    score +=

        Math.min(gain,35);

    const volume =

        parseFloat(

            String(coin.volume)

            .replace(/[$,MKB ]/g,"")

        ) || 0;

    score +=

        Math.min(volume,20);

    if(

        coin.holders

    ){

        score += 20;

    }

    if(

        coin.age

    ){

        score += 10;

    }

    if(

        coin.marketCap

    ){

        score += 15;

    }

    return Math.min(

        Math.round(score),

        100

    );

},
/* ======================================================
   Production Engine
====================================================== */

config:{

    scannerFile:"scanner.json",

    refreshMinutes:5,

    topCoins:5,

    apiVersion:"1.0"

},

log(message){

    console.log(

        `[AI Bakery] ${message}`

    );

},

formatCurrency(value){

    if(value===undefined || value===null){

        return "--";

    }

    return new Intl.NumberFormat(

        "en-US",

        {

            notation:"compact",

            maximumFractionDigits:2

        }

    ).format(Number(value));

},

formatPercent(value){

    if(value===undefined){

        return "--";

    }

    return `${Number(value).toFixed(2)}%`;

},

formatAge(minutes){

    if(minutes<60){

        return `${minutes}m`;

    }

    if(minutes<1440){

        return `${Math.floor(minutes/60)}h`;

    }

    return `${Math.floor(minutes/1440)}d`;

},

saveCache(data){

    try{

        localStorage.setItem(

            "catloaf_scanner",

            JSON.stringify(data)

        );

    }

    catch(e){}

},

loadCache(){

    try{

        return JSON.parse(

            localStorage.getItem(

                "catloaf_scanner"

            )

        );

    }

    catch(e){

        return [];

    }

},

updateTimestamp(){

    const now=new Date();

    const el=document.getElementById(

        "last-update"

    );

    if(el){

        el.textContent=

            now.toLocaleTimeString();

    }

}
/* ==========================================================
   AI Bakery Scanner
========================================================== */

async function loadScanner() {

    try {

        const response = await fetch("scanner/scanner.json");

        const data = await response.json();

        renderScanner(data);

    }

    catch(error){

        console.error(error);

    }

}

function renderScanner(data){

    const container = document.getElementById("scanner-container");

    if(!container) return;

    container.innerHTML = "";

    data.coins.forEach(coin=>{

        container.innerHTML += createCoinCard(coin);

    });

}