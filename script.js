"use strict";

/* ==========================================================
   CatLoaf AI Bakery
   script.js
========================================================== */

const CONFIG = {

    scannerFile: "scanner/scanner.json",

    refreshInterval: 5 * 60 * 1000,

    sparkBars: 12

};

const Bakery = {

    scannerContainer: null,

    scannerCount: null,

    lastUpdate: null,

    scannerData: [],

    refreshTimer: null,

    init() {

        console.log("🍞 CatLoaf AI Bakery Started");

        this.cacheDOM();

        this.updateClock();

        this.animateNewsCounter();

        this.fetchScanner();

        this.startAutoRefresh();

        setInterval(() => {

            this.updateClock();

}, 1000);

    },

    cacheDOM() {

        this.scannerContainer =

            document.getElementById(

                "scanner-container"

            );

        this.scannerCount =

            document.getElementById(

                "scanner-count"

            );

        this.lastUpdate =

            document.getElementById(

                "last-update"

            );

    },

    async fetchScanner() {

        if (!this.scannerContainer) return;

        this.showLoading();

        try {

            const response = await fetch(

                CONFIG.scannerFile +

                "?t=" +

                Date.now(),

                {

                    cache: "no-store"

                }

            );

            if (!response.ok) {

                throw new Error(

                    "Unable to load scanner.json"

                );

            }

            const json =

                await response.json();

            this.scannerData =

                json.coins || [];

            this.updateSummary(

                json.last_updated

            );

            this.renderScanner();

        }

        catch (error) {

            console.error(error);

            this.showError();

        }

    },

    startAutoRefresh() {

        this.refreshTimer = setInterval(() => {

            this.fetchScanner();

        },

        CONFIG.refreshInterval);

    },
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

                    AI Bakery is baking today's rankings...

                </p>

            </div>

        `;

    },

    showError() {

        this.scannerContainer.innerHTML = `

            <div class="scanner-empty">

                <h3>

                    ⚠ Scanner Offline

                </h3>

                <p>

                    Unable to retrieve today's launches.

                    The Bakery will try again automatically.

                </p>

            </div>

        `;

    },

    updateSummary(lastUpdated) {

        if (this.scannerCount) {

            this.scannerCount.textContent =

                this.scannerData.length;

        }

        if (this.lastUpdate) {

            this.lastUpdate.textContent =

                lastUpdated || "Waiting for first scan";

        }

    },
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
                    🥇 #${coin.rank || index + 1}
                </div>

                <div class="coin-header">

                    <img
                        class="coin-logo"
                        src="${coin.logo || "assets/logo.jpg"}"
                        alt="${coin.name}"
                    >

                    <div class="coin-info">

                        <div class="coin-name">

                            ${coin.name}

                        </div>

                        <div class="coin-symbol">

                            $${coin.symbol}

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

                        <small>Market Cap</small>

                        <strong>

                            ${this.formatCompact(coin.market_cap)}

                        </strong>

                    </div>

                    <div class="stat">

                        <small>Volume</small>

                        <strong>

                            ${this.formatCompact(coin.volume)}

                        </strong>

                    </div>

                    <div class="stat">

                        <small>Holders</small>

                        <strong>

                            ${coin.holders}

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

<div class="ai-verdict">

    <h4>🤖 AI Bakery Verdict</h4>

    <div class="ai-tags">

        <span class="tag">

            🚀 ${coin.momentum}

        </span>

        <span class="tag">

            ⚠️ ${coin.risk}

        </span>

        <span class="tag">

            ⭐ ${coin.opportunity}

        </span>

    </div>

    <p class="verdict">

        ${coin.verdict}

    </p>

</div>

<div class="coin-footer">

                    <span>

                        Updated

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

            this.scannerContainer.appendChild(card);

        });

    },
    /* ======================================================
       Helper Functions
    ====================================================== */

    generateSparkline() {

        let html = "";

        for (let i = 0; i < CONFIG.sparkBars; i++) {

            const height =

                Math.floor(Math.random() * 45) + 30;

            html += `

                <span
                    class="spark"
                    style="height:${height}%"
                ></span>

            `;

        }

        return html;

    },

    formatPrice(price) {

        if (price === undefined || price === null) {

            return "--";

        }

        const value = Number(price);

        if (value === 0) {

            return "--";

        }

        if (value < 0.01) {

            return "$" + value.toFixed(6);

        }

        if (value < 1) {

            return "$" + value.toFixed(4);

        }

        return "$" + value.toFixed(2);

    },

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

    formatPercent(value) {

        if (value === undefined || value === null) {

            return "--";

        }

        const number = Number(value);

        return `${number >= 0 ? "+" : ""}${number.toFixed(2)}%`;

    },
updateClock() {

    const clock = document.getElementById("bakery-time");

    if (!clock) return;

    const now = new Date();

    clock.textContent = now.toLocaleTimeString([], {

        hour: "2-digit",

        minute: "2-digit"

    });

},

animateNewsCounter() {

    const counter = document.querySelector("[data-count]");

    if (!counter) return;

    const target = Number(counter.dataset.count);

    let current = 0;

    const timer = setInterval(() => {

        current++;

        counter.textContent = current;

        if (current >= target) {

            clearInterval(timer);

        }

    }, 80);

},

    copyCA() {

        const ca = document.getElementById("ca");

        if (!ca) return;

        navigator.clipboard.writeText(

            ca.textContent.trim()

        );

        alert("✅ Contract Address Copied");

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