# Versi Riflessi

Un piccolo sito web dove trovano posto le mie poesie.

## 📁 Struttura del Progetto

```
versi_riflessi/
├── code/                      # 💻 Sorgenti per lo sviluppo
│   ├── full.html              # HTML modulare per sviluppo locale
│   ├── styles/
│   │   └── style.css          # Fogli di stile CSS
│   └── scripts/
│       ├── poesie.js          # Dati e testi delle poesie
│       ├── applicazione.js    # Logica applicativa e UI
│       └── service-worker.js  # Sorgente Service Worker
├── images/                    # 🖼️ Risorse grafiche e icone
│   ├── favicon.ico
│   ├── logo-192.png
│   ├── logo-512.png
│   └── qr-code.png
├── hooks/                     # ⚙️ Script di build e Git Hook
│   ├── minimize.py            # Build & minimizzazione (code/ -> index.html + SW)
│   └── pre-commit             # Hook Git eseguito prima di ogni commit
├── index.html                 # 🚀 Bundle di deploy (ultra-minimizzato, single-file inline)
├── service-worker.js          # 🚀 Service worker minimizzato per root scope
└── manifest.json              # 🚀 Web App Manifest PWA
```

## 🛠️ Sviluppo e Build

- **Sviluppo:** Modifica direttamente i file nella cartella `code/` (`code/full.html`, `code/styles/style.css`, `code/scripts/poesie.js`, `code/scripts/applicazione.js`).
- **Build manuale:**
  ```bash
  python3 hooks/minimize.py
  ```
- **Git Hook automatico:**
  L'hook di `pre-commit` è configurato per compilare e minimizzare automaticamente `index.html` e `service-worker.js` prima di ogni commit:
  ```bash
  git config core.hooksPath hooks
  ```
