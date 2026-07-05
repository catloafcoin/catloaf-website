/* ==========================================================
   CatLoaf AI Bakery
   script.js
   Version 2.0
   Part 1 - Core Engine
========================================================== */

"use strict";

const Bakery = {

    version: "2.0.0",

    refreshMinutes: 5,

    scannerData: [],

    scannerElement: null,

    lastUpdateElement: null,

    clockElement: null,

    /* ======================================================
       Initialize
    ====================================================== */

    init() {

        console.log("🍞 CatLoaf AI Bakery Started");

        this.cacheDOM();

        this.startClock();

        this.animateCounters();

        this.observeCards();

        this.startScanner();

    },

    /* ======================================================
       Cache DOM
    ====================================================== */

    cacheDOM() {

        this.scannerElement =
            document.getElementById(
                "scanner-container"
            );

        this.lastUpdateElement =
            document.getElementById(
                "last-update"
            );

        this.clockElement =
            document.getElementById(
                "bakery-time"
            );

    },

    /* ======================================================
       Live Clock
    ====================================================== */

    startClock() {

        const updateClock = () => {

            if (!this.clockElement) return;

            this.clockElement.textContent =
                new Date().toLocaleTimeString();

        };

        updateClock();

        setInterval(updateClock,1000);

    },

    /* ======================================================
       Animated Counters
    ====================================================== */

    animateCounters() {

        document

            .querySelectorAll("[data-count]")

            .forEach(counter=>{

                const target =

                    Number(counter.dataset.count);

                let current = 0;

                const step =

                    Math.max(1,target/40);

                const timer = setInterval(()=>{

                    current += step;

                    if(current >= target){

                        current = target;

                        clearInterval(timer);

                    }

                    counter.textContent =

                        Math.floor(current);

                },25);

            });

    },

    /* ======================================================
       Scroll Reveal
    ====================================================== */

    observeCards() {

        const observer =

            new IntersectionObserver(entries=>{

                entries.forEach(entry=>{

                    if(entry.isIntersecting){

                        entry.target.classList.add("show");

                    }

                });

            },{

                threshold:0.12

            });

        document

            .querySelectorAll(

                ".card,.status-item"

            )

            .forEach(card=>{

                card.classList.add("fade-in");

                observer.observe(card);

            });

    },

    /* ======================================================
       Scanner Bootstrap
    ====================================================== */

    startScanner(){

        this.fetchScannerData();

        setInterval(()=>{

            this.fetchScannerData();

        },this.refreshMinutes*60*1000);

    },

    /* ======================================================
       Fetch Scanner JSON
       (continues in Part 2)
    ====================================================== */

    async fetchScannerData() {

        if (!this.scannerElement) return;

        try {

            const response = await fetch(

                "scanner/scanner.json?ts=" + Date.now(),

                {
                    cache: "no-store"
                }

            );

            if (!response.ok) {

                throw new Error("Unable to load scanner.json");

            }

            const data = await response.json();

            this.scannerData = data.coins || [];

            this.renderScanner(this.scannerData);

            this.updateLastUpdated(data.last_updated);

            console.log("✅ Scanner updated");

        }

        catch (error) {

            console.error(error);

            this.showScannerError();

        }

    },

    /* ======================================================
       Update Timestamp
    ====================================================== */

    updateLastUpdated(time) {

        if (!this.lastUpdateElement) return;

        if (!time) {

            this.lastUpdateElement.textContent =
                "Waiting for first scan...";

            return;

        }

        this.lastUpdateElement.textContent = time;

    },

    /* ======================================================
       Scanner Error
    ====================================================== */

    showScannerError() {

        if (!this.scannerElement) return;

        this.scannerElement.innerHTML = `

        <div class="scanner-loading">

            <div class="loading-loaf">

                ⚠️

            </div>

            <h3>

                Scanner Offline

            </h3>

            <p>

                The Bakery couldn't load today's launches.

                It will automatically try again.

            </p>

        </div>

        `;

    },

    /* ======================================================
       Render Scanner
    ====================================================== */

    renderScanner(coins) {

        if (!this.scannerElement) return;

        this.scannerElement.innerHTML = "";

        coins.forEach((coin, index) => {

            this.scannerElement.innerHTML +=
                this.createCoinCard(coin, index + 1);

        });

    },

    /* ======================================================
       Coin Card Generator
       (continues in Part 3)
    ====================================================== */

    createCoinCard(coin, rank) {

        return `

        <div class="coin-card">

            <div class="coin-header">

                <img
                    class="coin-logo"
                    src="${coin.logo || "assets/logo.jpg"}"
                    alt="${coin.name}"
                    onerror="this.src='assets/logo.jpg'"
                >

                <div style="flex:1;">

                    <div class="coin-name">

                        ${coin.name}

                    </div>

                    <div class="coin-symbol">

                        $${coin.symbol}

                    </div>

                </div>

                <div class="coin-rank">

                    🥇 #${rank}

                </div>

            </div>

            <div class="coin-price">

                $${this.formatPrice(coin.price)}

            </div>

            <div class="coin-change ${coin.change24h >= 0 ? "gain" : "loss"}">

                ${coin.change24h >= 0 ? "📈" : "📉"}
                ${this.formatPercent(coin.change24h)}

            </div>

            <div class="coin-stats">

                <div class="stat">

                    <small>Market Cap</small>

                    <strong>

                        $${this.formatCompact(coin.market_cap)}

                    </strong>

                </div>

                <div class="stat">

                    <small>Volume</small>

                    <strong>

                        $${this.formatCompact(coin.volume)}

                    </strong>

                </div>

                <div class="stat">

                    <small>Holders</small>

                    <strong>

                        ${this.formatCompact(coin.holders)}

                    </strong>

                </div>

                <div class="stat">

                    <small>Age</small>

                    <strong>

                        ${coin.age_hours}h

                    </strong>

                </div>

            </div>

            <div class="loaf-title">

                <span>

                    🍞 Loaf Score

                </span>

                <strong>

                    ${coin.loaf_score}/100

                </strong>

            </div>

            <div class="loaf-bar">

                <div
                    class="loaf-fill"
                    style="width:${coin.loaf_score}%"
                ></div>

            </div>

            <div class="sparkline">

                ${this.generateSparkline()}

            </div>

            <div class="coin-footer">

                <small>

                    Updated just now

                </small>

                <a

                    href="${coin.url}"

                    target="_blank"

                    class="view-btn"

                >

                    🚀 View

                </a>

            </div>

        </div>

        `;

    },

    /* ======================================================
       Utility Functions
       (continues in Part 4)
    ====================================================== */

    formatCompact(value) {

        if (value === undefined || value === null) {

            return "--";

        }

        return new Intl.NumberFormat(

            "en-US",

            {

                notation: "compact",

                maximumFractionDigits: 2

            }

        ).format(Number(value));

    },

    /* ======================================================
       Price Formatter
    ====================================================== */

    formatPrice(value) {

        if (value === undefined || value === null) {

            return "0.000000";

        }

        return Number(value).toFixed(6);

    },

    /* ======================================================
       Percent Formatter
    ====================================================== */

    formatPercent(value) {

        if (value === undefined || value === null) {

            return "0.00%";

        }

        const number = Number(value);

        return `${number > 0 ? "+" : ""}${number.toFixed(2)}%`;

    },

    /* ======================================================
       Sparkline Generator
    ====================================================== */

    generateSparkline() {

        let html = "";

        for (let i = 0; i < 16; i++) {

            const height =

                Math.floor(

                    Math.random() * 55

                ) + 30;

            html += `

                <span
                    class="spark"
                    style="height:${height}%"
                ></span>

            `;

        }

        return html;

    },

    /* ======================================================
       Copy Contract Address
    ====================================================== */

    copyContract() {

        const contract = document.getElementById("ca");

        if (!contract) return;

        navigator.clipboard.writeText(

            contract.textContent.trim()

        );

        alert("🍞 Contract Address Copied!");

    },

    /* ======================================================
       End of Utilities
       (continues in Part 5)
    ====================================================== */

};

/* ==========================================================
   Global Functions
========================================================== */

function copyCA() {

    Bakery.copyContract();

}

/* ==========================================================
   Launch Bakery
========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    () => {

        Bakery.init();

    }

);