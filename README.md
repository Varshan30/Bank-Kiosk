# Bank Kiosk Demo

A minimal banking kiosk + auth demo.

## Features
- User signup/login with 4-digit passcode (demo only; plaintext stored).
- MySQL `auth_users` table auto-created.
- Deposit / Withdraw / Balance endpoints (simple JSON).
- Frontend single-page kiosk with denomination calculator and time-limited code generation.

## Tech
- Frontend: Vanilla HTML/CSS/JS (`index.html`)
- Backend: Flask + MySQL (`app.py`)

## Quick Start
```bash
# 1. (Windows PowerShell) Create/activate venv (optional)
python -m venv venv
./venv/Scripts/Activate.ps1

# 2. Install deps
pip install -r requirements.txt

# 3. Ensure MySQL database exists
# Create DB if not already:
#   CREATE DATABASE bank_kiosk;

# 4. Run server
python app.py

# 5. Open frontend (double-click or via simple server)
#   python -m http.server 8000 (then open http://localhost:8000/index.html)
```

## Environment Variables (optional future)
For production, move credentials out of source and into environment variables.

## Security Notes
- Passcodes are stored plaintext (demo). Use a hashing library (bcrypt) before real use.
- No rate limiting / JWT tokens yet.

## License
MIT (add LICENSE file if distributing).
