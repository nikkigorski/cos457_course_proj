# Flask API for LobsterNotes

This small Flask app exposes a JSON REST API for the LobsterNotes MySQL schema.

Setup (development):

1. Create virtualenv and install deps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your database credentials

3. Run the server

```bash
python app.py
```

By default the server listens on port `4000`. Endpoints are under `/api/*`.

Integration: set your frontend's API base to `http://localhost:4000/api` during development.
