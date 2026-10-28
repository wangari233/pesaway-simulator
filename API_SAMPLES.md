# Day 4: Payments API samples

Base URL: `http://127.0.0.1:8000`. Tested with `curl.exe` in PowerShell.

## CSRF

`CsrfViewMiddleware` stays enabled and `@csrf_exempt` is not used. POST and PATCH need
a `csrftoken` cookie plus the same value in an `X-CSRFToken` header. A GET to
`/payments/` sets the cookie (`@ensure_csrf_cookie`).

## Success cases

| Request | Response |
|---|---|
| `GET /payments/` | `200` `{"payments": [{"id": 5, "reference": "TXN010", ...}, ...]}` (newest first) |
| `GET /payments/?status=PENDING` | `200` only payments with status PENDING |
| `GET /payments/?status=failed` | `200` only TXN001 (filter is case-insensitive) |
| `GET /payments/2/` | `200` `{"id": 2, "reference": "TXN001", "amount": "500.00", "currency": "USD", "status": "FAILED", "created_at": "2026-10-21T13:06:25.098642+00:00"}` |
| `POST /payments/` `{"reference":"TXN010","amount":"750.00","currency":"KES"}` | `201` `{"id": 5, "reference": "TXN010", "amount": "750.00", "currency": "KES", "status": "PENDING", "created_at": "2026-10-26T08:12:52.239428+00:00"}` |
| `PATCH /payments/3/` `{"amount":"300.00"}` | `200` `{"id": 3, "reference": "TXN002", "amount": "300.00", "currency": "KES", "status": "PENDING", ...}` |

## Failure cases

| Request | Response |
|---|---|
| `POST /payments/` with no CSRF token | `403 Forbidden` (Django's HTML CSRF failure page) |
| `POST` duplicate reference | `409` `{"error": "A payment with this reference already exists"}` |
| `POST` body `{"reference":"X1"` | `400` `{"error": "Malformed JSON body"}` |
| `POST` `{"reference":"","amount":-5,"currency":"KES"}` | `400` `{"error": "Validation failed", "fields": {"reference": "required, non-empty string", "amount": "amount must be greater than 0"}}` |
| `POST` with `"status":"COMPLETED"` | `400` `{"error": "Validation failed", "fields": {"status": "cannot be set; new payments always start as PENDING"}}` |
| `POST` `{"reference":"TXN012","amount":"abc"}` | `400` `{"error": "Validation failed", "fields": {"amount": "amount must be a number", "currency": "required, 3-letter code such as KES"}}` |
| `GET /payments/?status=BOGUS` | `400` `{"error": "Invalid status filter", "allowed": ["PENDING", "COMPLETED", "FAILED"]}` |
| `GET /payments/9999/` | `404` `{"error": "Payment not found"}` |
| `PATCH /payments/3/` `{"status":"COMPLETED"}` | `400` `{"error": "status cannot be changed through this endpoint"}` |
| `PATCH /payments/3/` `{"reference":"HACK"}` | `400` `{"error": "Fields not editable", "fields": ["reference"]}` |
| `PATCH /payments/3/` `{}` | `400` `{"error": "No fields to update"}` |
| `PATCH /payments/3/` `{"amount":"-1"}` | `400` `{"error": "Validation failed", "fields": {"amount": "amount must be greater than 0"}}` |
| `PATCH /payments/9999/` | `404` `{"error": "Payment not found"}` |
| `DELETE /payments/3/` | `405 Method Not Allowed` |