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

## Endpoints

| Method | URL | What it does | Success | Failure cases |
|---|---|---|---|---|
| GET | `/payments/` | Lists payments, newest first; optional `?status=` filter | `200` | `400` for an invalid status filter |
| POST | `/payments/` |Creates a payment from `reference`, `amount` and `currency`; new payments always start as `PENDING` |`201` |`403` missing CSRF token; `409` duplicate reference; `400` malformed JSON; `400` validation failed (bad amount, missing field, or `status` sent) |
| GET | `/payments/<id>/` |Returns one payment |`200` |`404` unknown ID |
| PATCH | `/payments/<id>/` | Updates `amount` or `currency` only |`200` |`404` unknown ID; `400` if `status` or another non-editable field is sent, the body is empty, or a value is invalid |


Full sample requests and responses, including every failure case, are in [API_SAMPLES.md](API_SAMPLES.md). There is no DELETE endpoint.


## Running the tests

```powershell
python manage.py test payments_app
```

The seven tests cover: valid creation, a duplicate `reference` (only one payment is stored), an invalid amount, invalid JSON, an unknown ID (GET and PATCH return 404), a disallowed `status` update (the stored status stays unchanged), and CSRF enforcement (a POST without a token returns 403).

## Demo: duplicate reference

The `demo/` folder shows the same payment (`DEMO002`) sent twice against the running server:

- `1_first_post_201.txt`: the first request returns `201 Created`.
- `2_second_post_409.txt`: the identical second request returns `409 Conflict`.
- `3_row_count.txt`: only one row with that reference exists in the database.