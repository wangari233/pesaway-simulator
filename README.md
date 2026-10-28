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


## How a request travels

Example: `POST /payments/` with a new payment.

1. The client sends a `POST` request to `/payments/` with the headers `Content-Type: application/json` and `X-CSRFToken`, and a JSON body containing `reference`, `amount` and `currency`.
2. Django passes the request through its middleware first. `CsrfViewMiddleware` checks the token, and a request without a valid one is rejected with `403` before it reaches any of my code.
3. `pesaway_simulator/urls.py` sends paths that start with `payments/` to `payments_app/api_urls.py`, which maps `/payments/` to the `payment_list` view in `api_views.py`.
4. The view reads the body with `parse_json`. If the body is broken JSON, or is not a JSON object, it returns `400` straight away.
5. The view validates each field: `reference` must be a non-empty string, `amount` must be a positive number with at most two decimal places, `currency` must be a 3-letter code, and `status` must not be sent. If anything is wrong, it returns `400` with a message for each bad field, and nothing is saved.
6. The view calls `Payment.objects.create(...)` inside `transaction.atomic()`. The ORM turns this into an SQL `INSERT`, and the unique constraint on `reference` makes the database refuse a duplicate. The view catches that `IntegrityError`, and the `atomic()` block keeps the rest of the transaction usable.
7. The view builds a JSON response. A new payment returns `201` with the stored payment (its `status` is `PENDING`), and a duplicate reference returns `409` with an error message. The response travels back through the middleware to the client.