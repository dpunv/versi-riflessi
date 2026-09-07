document.addEventListener("DOMContentLoaded", () => {
    // ========================================
    // THEME SWITCHER LOGIC
    // ========================================
    const themeToggle = document.getElementById("theme-toggle");
    const htmlEl = document.documentElement;

    const applyTheme = (theme) => {
        htmlEl.classList.toggle("dark-mode", theme === "dark");
    };

    const savedTheme =
        localStorage.getItem("theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light");
    applyTheme(savedTheme);

    themeToggle.addEventListener("click", () => {
        const isDarkMode = htmlEl.classList.contains("dark-mode");
        const newTheme = isDarkMode ? "light" : "dark";
        applyTheme(newTheme);
        localStorage.setItem("theme", newTheme);
    });

    // ========================================
    // MAIN APPLICATION LOGIC
    // ========================================
    const contentSections = document.querySelectorAll(
        ".content-viewer > section",
    );
    const poemsToc = document.getElementById("poems-toc");
    const poemDisplayArea = document.getElementById("poem-display-area");
    const searchInput = document.getElementById("search-input");
    const logoLink = document.getElementById("logo-link");
    const mobileToggle = document.getElementById("mobile-toggle");
    const panelContent = document.getElementById("panel-content");

    const welcomeMessageHTML = poemDisplayArea.innerHTML;

    // --- 1. Populate Table of Contents ---
    poems.sort((a, b) => new Date(a.date) - new Date(b.date));
    poemsToc.innerHTML = poems
        .map(
            (poem) => `
    <li><a href="#${poem.id}" data-poem-id="${poem.id}">${poem.title}</a></li>
`,
        )
        .join("");

    const tocLinks = poemsToc.querySelectorAll("a");

    // --- 2. Core Functions ---
    const displayPoem = (poemId) => {
        const poem = poems.find((p) => p.id === poemId);
        if (!poem) return;

        // Creiamo l'HTML delle note solo se la nota esiste
        const noteHTML = poem.note
            ? `<div class="poem-notes">
                <strong>Nota dell'autore:</strong><br>
                ${poem.note}
            </div>`
            : "";

        const poemHTML = `
        <article class="poem-display">
            <h2 id="active-poem-title">${poem.title}</h2>
            <p class="poem-meta">${new Date(poem.date).toLocaleDateString("it-IT", { year: "numeric", month: "long", day: "numeric" })}</p>
            <div class="poem-text">
                ${poem.lines.map((line) => `<div>${line || "&nbsp;"}</div>`).join("")}
            </div>
            ${noteHTML}
        </article>
    `;
        poemDisplayArea.innerHTML = poemHTML;

        // --- LOGICA DEI 5 CLICK ---
        const titleElement = document.getElementById("active-poem-title");
        const notesElement = poemDisplayArea.querySelector(".poem-notes");
        let clickCount = 0;

        // Se ci sono note e il titolo esiste, aggiungiamo il listener
        if (titleElement && notesElement) {
            titleElement.addEventListener("click", () => {
                clickCount++;

                // Se arriviamo a 5 click
                if (clickCount === 5) {
                    notesElement.classList.add("revealed");
                    // Opzionale: scrolla leggermente verso le note per far vedere che sono apparse
                    notesElement.scrollIntoView({
                        behavior: "smooth",
                        block: "nearest",
                    });
                    clickCount = 0; // Reset del contatore
                }
            });
        }

        tocLinks.forEach((link) =>
            link.classList.toggle("active", link.dataset.poemId === poemId),
        );
    };

    const switchView = (viewId) => {
        contentSections.forEach((section) =>
            section.classList.toggle("active", section.id === viewId),
        );
    };

    const resetToHomeView = () => {
        switchView("poems-view");
        poemDisplayArea.innerHTML = welcomeMessageHTML;
        tocLinks.forEach((link) => {
            link.classList.remove("active");
            link.parentElement.style.display = "";
        });
        searchInput.value = "";
        history.pushState(
            "",
            document.title,
            window.location.pathname + window.location.search,
        );
    };

    const toggleMobilePanel = () => {
        const isExpanded = panelContent.classList.contains("expanded");
        panelContent.classList.toggle("expanded");
        mobileToggle.classList.toggle("expanded");

        mobileToggle.setAttribute("aria-expanded", !isExpanded);
    };

    const closeMobilePanelIfOpen = () => {
        if (
            window.innerWidth <= 900 &&
            panelContent.classList.contains("expanded")
        ) {
            panelContent.classList.remove("expanded");
            mobileToggle.classList.remove("expanded");
            mobileToggle.setAttribute("aria-expanded", "false");
        }
    };

    // --- 3. Event Listeners ---
    logoLink.addEventListener("click", (e) => {
        e.preventDefault();
        resetToHomeView();
        closeMobilePanelIfOpen();
    });

    mobileToggle.addEventListener("click", toggleMobilePanel);

    poemsToc.addEventListener("click", (e) => {
        if (e.target.tagName === "A" && e.target.dataset.poemId) {
            e.preventDefault();
            switchView("poems-view");
            displayPoem(e.target.dataset.poemId);
            window.location.hash = e.target.hash;
            closeMobilePanelIfOpen();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 900) {
            panelContent.classList.remove("expanded");
            mobileToggle.classList.remove("expanded");
            mobileToggle.setAttribute("aria-expanded", "false");
        }
    });

    // ========================================
    // EASTER EGG LOGIC
    // ========================================

    searchInput.addEventListener("input", (e) => {
        const searchTerm = e.target.value.toLowerCase();

        if (searchTerm.trim() === "lettere") {
            triggerEasterEgg();
            return;
        }

        poems.forEach((poem) => {
            const title = poem.title.toLowerCase();
            const content = poem.lines.join(" ").toLowerCase();
            const isMatch =
                title.includes(searchTerm) || content.includes(searchTerm);

            const linkElement = poemsToc.querySelector(
                `[data-poem-id="${poem.id}"]`,
            );
            if (linkElement) {
                linkElement.parentElement.style.display = isMatch ? "" : "none";
            }
        });
    });

    const triggerEasterEgg = () => {
        const targets = [
            document.querySelector(".site-header"),
            document.querySelector(".left-panel"),
            ...document.querySelectorAll(".content-viewer > section"),
            document.querySelector(".site-footer"),
        ];

        const windowHeight = window.innerHeight;

        targets.forEach((el) => {
            if (el && getComputedStyle(el).display !== "none") {
                const rect = el.getBoundingClientRect();

                let distanceToBottom = windowHeight - rect.bottom;

                const pileRandomness = Math.random() * 80;
                const finalDrop = Math.max(0, distanceToBottom - pileRandomness);

                const randomDeg = Math.random() * 20 - 10;

                el.style.setProperty("--fall-distance", `${finalDrop}px`);
                el.style.setProperty("--fall-rotate", `${randomDeg}deg`);

                el.classList.add("falling-element");
            }
        });

        setTimeout(() => {
            document
                .getElementById("secret-poem-overlay")
                .classList.add("visible");
        }, 1500);
    };

    // RESET FUNCTION
    const resetBtn = document.getElementById("reset-site-btn");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            document
                .getElementById("secret-poem-overlay")
                .classList.remove("visible");
            const targets = document.querySelectorAll(".falling-element");
            targets.forEach((el) => {
                el.classList.remove("falling-element");
                el.style.removeProperty("--fall-distance");
                el.style.removeProperty("--fall-rotate");
                el.style.transform = "";
            });
            searchInput.value = "";
            searchInput.focus();
            const allLinks = poemsToc.querySelectorAll("li");
            allLinks.forEach((li) => (li.style.display = ""));
        });
    }

    // --- 4. Handle Initial Page Load ---
    const currentHash = window.location.hash.substring(1);
    const poemLink = Array.from(tocLinks).find(
        (link) => link.hash === `#${currentHash}`,
    );

    if (poemLink) {
        switchView("poems-view");
        displayPoem(poemLink.dataset.poemId);
    } else {
        switchView("poems-view");
    }
});

// Modal QR Code
const qrModal = document.getElementById("qr-modal");
const qrTrigger = document.querySelector(".qr-img");

if (qrTrigger && qrModal) {
    qrTrigger.addEventListener("click", () => {
        qrModal.classList.add("active");
    });

    qrModal.addEventListener("click", () => {
        qrModal.classList.remove("active");
    });
}

// Service Worker Registration
if ("serviceWorker" in navigator) {
    navigator.serviceWorker
        .register("service-worker.js")
        .then(() => console.log("Service Worker registered"))
        .catch((err) => console.error("SW registration failed:", err));
}
