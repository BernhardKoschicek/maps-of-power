# 🗺️ Maps of Power

The research initiative **Maps of Power** serves the methodological and interdisciplinary networking of scholars in the field of *Historical Geography*.
Founded in 2019 under the title **"Maps of Power: Historical Atlas of Places, Borderzones and Migration Dynamics in Byzantium (TIB Balkans)"**, it emerged from the idea of deepening historical-geographical research methodologically and broadening it thematically.

Building on the long-running project **[Tabula Imperii Byzantini (TIB)](https://tib.oeaw.ac.at/)** — conducted at the *Austrian Academy of Sciences (Vienna)* since 1966 — the initiative aims to expand the spatial focus of the TIB beyond the Byzantine world to include other European regions of the Middle Ages.

The successfully completed cluster project **["Digitising Patterns of Power (DPP): Peripherical Mountains in the Medieval World"](https://dpp.oeaw.ac.at/)** can be seen as a methodological and conceptual precursor to this work.

---

## ⚙️ Installation

### Prerequisites
Make sure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+ and npm](https://nodejs.org/)
- ImageMagick (for `libmagickwand-dev`)

On Debian/Ubuntu systems, you can install dependencies via:
```bash
sudo apt install libmagickwand-dev python3 python3-venv nodejs npm
```

### Clone and set up the repository
```bash
# Clone the repository
git clone https://github.com/BernhardKoschicek/maps-of-power.git
cd maps-of-power
```

### Python-Setup mit uv
```bash
# uv installieren (siehe https://docs.astral.sh/uv/)
# Python-Version für das Projekt setzen und Abhängigkeiten installieren
uv python pin 3.10
uv sync
```

### Frontend setup
```bash
cd mop/static
npm install
```

### Run the project
```bash
# Backend (Flask)
uv run python runserver.py

# Frontend (falls benötigt)
npm run dev
```

---

## 📁 Project Structure

```
maps-of-power/
├── mop/                # Core application directory
│   ├── static/         # Frontend (JS/CSS assets)
│   ├── templates/      # HTML templates
│   └── ...
├── requirements.txt    # Python dependencies
├── package.json        # Frontend dependencies
└── README.md           # You are here
```

---

## 🧠 Development Status

> ⚠️ This project is currently a **work in progress (WIP)**.
> Expect frequent changes, experimental features, and evolving structures.

Contributions and feedback from the research and developer community are warmly welcome.

---

## 🧩 Related Projects

- [Tabula Imperii Byzantini (TIB)](https://tib.oeaw.ac.at/)
- [Digitising Patterns of Power (DPP)](https://dpp.oeaw.ac.at/)

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.
See the [LICENSE](./LICENSE) file for details.

---

## 🧑‍💻 Authors & Credits

Developed and maintained by the *Maps of Power* research group.
Hosted and supported by the **Austrian Academy of Sciences (ÖAW)**.
For inquiries or collaboration, please contact the project team.

---


### Tests & Coverage
```bash
# Unit-Tests mit Coverage ausführen
uv run pytest --cov=mop --cov-report=term-missing
```
