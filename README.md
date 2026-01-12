# AutoChess (Django + HTMX)

A small web application where **two pre-trained chess engines** play against each other.
The UI is intentionally minimal: left engine panel, center chessboard, right engine panel, plus a move list and match history.

This repository is generated to follow the **AutoChess** specification you provided. 

## Key characteristics

- **Backend**: Django
- **Frontend**: HTMX (no SPA build pipeline)
- **Engines**: UCI engines (MVP: Stockfish vs Stockfish)
- **Execution model**: A `tick` endpoint advances the game by exactly **one ply** (half-move) under a DB row lock.
- **Speed**: UI speed is a **move interval** (`move_interval_ms`), not engine think-time. 
- **Draw policy**: if a draw is claimable, the system **auto-claims** it to avoid infinite games. 

## python-chess használata (SVG tábla és bábuk)

A felületben a tábla és a bábuk **SVG-ként** jelennek meg a `python-chess` (`chess`) csomag `chess.svg` modulja segítségével. Ez stabil és platformfüggetlen megjelenítést ad (nem függ a rendszer betűkészleteitől), valamint támogatja az utolsó lépés és a sakk-jelzés vizuális kiemelését.

Fontos: a `python-chess` **GPLv3** licencű. Ha a projekted licencelési szempontból szigorú, akkor ezt a függőséget csak akkor használd, ha a copyleft feltételek elfogadhatók a számodra. (Lásd: `third_party_licences.md`.)

## Quick start (Windows 11 / Linux)

This project loads `.env` automatically via **python-dotenv** (see `manage.py`, `asgi.py`, `wsgi.py`).

1. Create venv and install deps:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS

   pip install -r requirements.txt
   ```

2. Install Stockfish (binary must be available on PATH or configured by env var)

   - Linux: install via your package manager (e.g. `apt install stockfish`), or download from Stockfish official site.
   - Windows: download a Stockfish build and set `AUTOCHESS_STOCKFISH_PATH` to the exe path.

3. Configure environment:

   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env   # Linux
   ```

   Then edit `.env` (especially `AUTOCHESS_STOCKFISH_PATH` if needed).

4. Migrate and run:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Open: http://127.0.0.1:8000/

## Hungarian summary (HU)

Ez egy Django + HTMX webapp, ahol két UCI-s sakkmotor (alapból Stockfish vs Stockfish) egymás ellen játszik.
A játék **tick** végponton keresztül léptethető: egy tick = egy fél-lépés, tranzakcióval és sorzárral.
A “sebesség” a **lépésköz**, nem a gondolkodási idő.

## License

GPL-3.0-only (project code). External components are listed in `docs/third_party_licenses.md`.



## Demo deployment notes (shared hosting / Hetzner Cloud)

This project **can** run on a small VM without Docker. For a demo with light traffic, keep it simple:

- Prefer **PostgreSQL** for production-like usage.
- If you keep **SQLite** (ok for demos), this repo enables:
  - `PRAGMA journal_mode=WAL` + `busy_timeout` (best effort) on startup,
  - `timeout=20s` on the Django SQLite connection,
  - a **per-game tick lock** (`Game.tick_lock`) to avoid double-tick races from multiple tabs.

### Recommended process model (no Docker)

Run a single app process to minimize SQLite contention:

- Gunicorn: `--workers 1 --threads 4` (or even `--threads 2`)
- Put it behind Nginx (optional for a demo).
- Use `collectstatic` and serve static files via Nginx (or Whitenoise if you prefer).

If you later observe real concurrency, migrate to PostgreSQL and scale workers normally.
