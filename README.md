# Pesaway Simulator

Pesaway Simulator is a small payment API built with Python and Django. It stores payments in a database, but no real money moves. Clients can create payments, list them (optionally filtered by status), view one payment, and update its amount or currency using JSON requests.

Every payment has a unique `reference`. If the same reference is sent twice, the second request is rejected and only one payment is stored.

## Setup (Windows, PowerShell)

Requires Python 3.14 and Django 6.1.2 (installed from `requirements.txt`).

```powershell
git clone <your-repo-url>
cd <repo-folder>
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/payments/`.
