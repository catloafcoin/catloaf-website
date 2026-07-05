/* ==========================================================
   CatLoaf AI Bakery
   script.js
   Production Edition
   Part 1
========================================================== */

"use strict";

/* ==========================================================
   Configuration
========================================================== */

const CONFIG = {

    scannerFile: "scanner/scanner.json",

    refreshInterval: 5 * 60 * 1000,

    animationSpeed: 800,

    sparkBars: 12,

    version: "2.0"

};

/* ==========================================================
   Bakery Application
========================================================== */

const Bakery = {

    scannerData: [],

    refreshTimer: null,

    /* ------------------------------------------------------ */

    init() {

        console.log("🍞 CatLoaf AI Bakery v" + CONFIG.version);

        this.cacheElements();

        this.startClock();

        this.animateCounters();

        this.observeCards();

        this.fetchScanner();

        this.startAutoRefresh();

    },

    /* ------------------------------------------------------ */

    cacheElements() {

        this.scannerContainer =
            document.getElementById("scanner-container");

        this.lastUpdate =
            document.getElementById("last-update");

        this.clock =
            document.getElementById("bakery-time");

        this.scannerCount =
            document.getElementById("scanner-count");

    },

    /* ======================================================
       Live Clock
    ====================================================== */

    startClock() {

        const update = () => {

            if (!this.clock) return;

            this.clock.textContent =
                new Date().toLocaleTimeString([], {

                    hour: "2-digit",

                    minute: "2-digit",

                    second: "2-digit"

                });

        };

        update();

        setInterval(update, 1000);

    },

    /* ======================================================
       Animated Counters
    ====================================================== */

    animateCounters() {

        document

            .querySelectorAll("[data-count]")

            .forEach(counter => {

                const target = Number(counter.dataset.count);

                let value = 0;

                const step = Math.max(1, target / 40);

                const timer = setInterval(() => {

                    value += step;

                    if (value >= target) {

                        value = target;

                        clearInterval(timer);

                    }

                    counter.textContent =

                        Math.floor(value);

                }, 25);

            });

    },

    /* ======================================================
       Scroll Reveal
    ====================================================== */

    observeCards() {

        const observer = new IntersectionObserver(

            entries => {

                entries.forEach(entry => {

                    if (entry.isIntersecting) {

                        entry.target.classList.add("show");

                    }

                });

            },

            {

                threshold: 0.15

            }

        );

        document

            .querySelectorAll(".card,.status-item")

            .forEach(card => {

                card.classList.add("fade-in");

                observer.observe(card);

            });

    },
    /* ======================================================
       Scanner Loader
    ====================================================== */

    async fetchScanner() {

        if (!this.scannerContainer) return;

        this.showLoading();

        try {

            const response = await fetch(

                CONFIG.scannerFile + "?t=" + Date.now(),

                {

                    cache: "no-store"

                }

            );

            if (!response.ok) {

                throw new Error(

                    "Unable to load scanner.json"

                );

            }

            const data = await response.json();

            this.scannerData =

                Array.isArray(data)

                ? data

                : (data.coins || []);

            this.updateSummary();

            this.renderScanner();

        }

        catch (error) {

            console.error(error);

            this.showError();

        }

    },

    /* ======================================================
       Auto Refresh
    ====================================================== */

    startAutoRefresh() {

        this.refreshTimer = setInterval(() => {

            this.fetchScanner();

        },

        CONFIG.refreshInterval);

    },

    /* ======================================================
       Loading Screen
    ====================================================== */

    showLoading() {

        this.scannerContainer.innerHTML = `

            <div class="scanner-loading">

                <div class="loading-loaf">

                    🍞

                </div>

                <h3>

                    Scanning fresh Pump.fun launches...

                </h3>

                <p>

                    AI Bakery is ranking today's strongest projects.

                </p>

            </div>

        `;

    },

    /* ======================================================
       Error Screen
    ====================================================== */

    showError() {

        this.scannerContainer.innerHTML = `

            <div class="scanner-empty">

                <h3>

                    ⚠ Scanner Offline

                </h3>

                <p>

                    Unable to load today's launches.

                    The Bakery will automatically retry.

                </p>

            </div>

        `;

    },

    /* ======================================================
       Summary Cards
    ====================================================== */

    updateSummary() {

        if (this.scannerCount) {

            this.scannerCount.textContent =

                this.scannerData.length;

        }

        if (this.lastUpdate) {

            this.lastUpdate.textContent =

                new Date().toLocaleTimeString([], {

                    hour: "2-digit",

                    minute: "2-digit"

                });

        }

    },
    /* ======================================================
       Render Scanner
    ====================================================== */

    renderScanner() {

        if (!this.scannerContainer) return;

        this.scannerContainer.innerHTML = "";

        if (this.scannerData.length === 0) {

            this.showError();

            return;

        }

        this.scannerData.forEach((coin, index) => {

            const card = document.createElement("div");

            card.className = "coin-card";

            card.innerHTML = `

                <div class="coin-rank">

                    🥇 #${index + 1}

                </div>

                <div class="coin-header">

                    <img
                        class="coin-logo"
                        src="${coin.logo || "assets/logo.jpg"}"
                        alt="${coin.name}"
                    >

                    <div>

                        <div class="coin-name">

                            ${coin.name}

                        </div>

                        <div class="coin-symbol">

                            ${coin.symbol}

                        </div>

                    </div>

                </div>

                <div class="coin-price">

                    ${this.formatPrice(coin.price)}

                </div>

                <div class="coin-change ${Number(coin.change24h) >= 0 ? "gain" : "loss"}">

                    ${this.formatPercent(coin.change24h)}

                </div>

                <div class="coin-stats">

                    <div class="stat">

                        <small>Volume</small>

                        <strong>

                            ${this.formatCompact(coin.volume)}

                        </strong>

                    </div>

                    <div class="stat">

                        <small>Market Cap</small>

                        <strong>

                            ${this.formatCompact(coin.market_cap)}

                        </strong>

                    </div>

                    <div class="stat">

                        <small>Holders</small>

                        <strong>

                            ${coin.holders || "--"}

                        </strong>

                    </div>

                    <div class="stat">

                        <small>Age</small>

                        <strong>

                            ${coin.age_hours ?? "--"}h

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

                    <span class="updated">

                        Updated just now

                    </span>

                    <a
                        class="view-btn"
                        href="${coin.url || "#"}"
                        target="_blank"
                    >

                        View →

                    </a>

                </div>

            `;

            this.scannerContainer.appendChild(card);

        });

    },
    /* ======================================================
       Sparkline Generator
    ====================================================== */

    generateSparkline() {

        let html = "";

        for (let i = 0; i < CONFIG.sparkBars; i++) {

            const height =

                Math.floor(Math.random() * 55) + 25;

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
       Price Formatter
    ====================================================== */

    formatPrice(price) {

        if (price === undefined || price === null) {

            return "--";

        }

        const value = Number(price);

        if (value < 0.01) {

            return "$" + value.toFixed(6);

        }

        if (value < 1) {

            return "$" + value.toFixed(4);

        }

        return "$" + value.toFixed(2);

    },

    /* ======================================================
       Compact Number Formatter
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
       Percent Formatter
    ====================================================== */

    formatPercent(value) {

        if (value === undefined || value === null) {

            return "--";

        }

        const number = Number(value);

        return `${number >= 0 ? "+" : ""}${number.toFixed(2)}%`;

    },

    /* ======================================================
       Copy Contract Address
    ====================================================== */

    copyCA() {

        const contract =

            document.getElementById("ca");

        if (!contract) return;

        navigator.clipboard

            .writeText(contract.innerText)

            .then(() => {

                alert("✅ Contract copied!");

            });

    },
};

/* ==========================================================
   Global Functions
========================================================== */

function copyCA() {

    Bakery.copyCA();

}

/* ==========================================================
   Start AI Bakery
========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    () => {

        Bakery.init();

    }

);