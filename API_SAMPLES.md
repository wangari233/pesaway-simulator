# Day 4: Payments API samples

Base URL: `http://127.0.0.1:8000`. Tested with `curl.exe` in PowerShell.

## CSRF

`CsrfViewMiddleware` stays enabled and `@csrf_exempt` is not used. POST and PATCH need
a `csrftoken` cookie plus the same value in an `X-CSRFToken` header. A GET to
`/payments/` sets the cookie (`@ensure_csrf_cookie`).

## Success cases

| Request | Response |
|---|---|
| `GET /payments/` | `200` `{"payments": [{"id": 10, "reference": "PSW-10001", ...}, ...]}` (newest first) |
| `GET /payments/?status=PENDING` | `200` only payments with status PENDING |
| `GET /payments/?status=SUCCESS` | `200` only TXN003 |
| `GET /payments/?status=failed` | `200` only TXN001 (filter is case-insensitive) |
| `GET /payments/2/` | `200` `{"id": 2, "reference": "TXN001", "amount": "500.00", "currency": "KES", "phone_number": "0700000000", "payment_method": "MOBILE_MONEY", "status": "FAILED", "created_at": "2026-10-21T13:06:25.098642+00:00"}` |
| `POST /payments/` `{"reference":"PSW-10001","amount":"1500.00","currency":"KES","phone_number":"254700000001","payment_method":"MOBILE_MONEY"}` | `201` `{"id": 10, "reference": "PSW-10001", "amount": "1500.00", "currency": "KES", "phone_number": "254700000001", "payment_method": "MOBILE_MONEY", "status": "PENDING", "created_at": "2026-10-30T09:08:17.701018+00:00"}` |
| `PATCH /payments/10/` `{"amount":"1600.00"}` | `200` same payment with `"amount": "1600.00"` (changed from 1500.00) and `"status": "PENDING"` |

## Failure cases

| Request | Response |
|---|---|
| `POST /payments/` with no CSRF token | `403 Forbidden` (Django's HTML CSRF failure page) |
| `POST` duplicate reference (the PSW-10001 body again) | `409` `{"error": "A payment with this reference already exists"}` |
| `POST` body `{"reference":"X1"` | `400` `{"error": "Malformed JSON body"}` |
| `POST` `{"reference":"","amount":-5,"currency":"KES"}` | `400` `{"error": "Validation failed", "fields": {"reference": "required, non-empty string", "amount": "amount must be greater than 0", "phone_number": "required, non-empty string", "payment_method": "required, one of: MOBILE_MONEY, BANK"}}` |
| `POST` valid body plus `"status":"SUCCESS"` | `400` `{"error": "Validation failed", "fields": {"status": "cannot be set; new payments always start as PENDING"}}` |
| `POST` `{"reference":"TXN012","amount":"abc"}` | `400` `{"error": "Validation failed", "fields": {"amount": "amount must be a number", "currency": "required, one of: KES, UGX", "phone_number": "required, non-empty string", "payment_method": "required, one of: MOBILE_MONEY, BANK"}}` |
| `GET /payments/?status=BOGUS` | `400` `{"error": "Invalid status filter", "allowed": ["PENDING", "SUCCESS", "FAILED"]}` |
| `GET /payments/9999/` | `404` `{"error": "Payment not found"}` |
| `PATCH /payments/10/` `{"status":"SUCCESS"}` | `400` `{"error": "status cannot be changed through this endpoint"}` (stored status stays PENDING) |
| `PATCH /payments/10/` `{"reference":"HACK"}` | `400` `{"error": "Fields not editable", "fields": ["reference"]}` |
| `PATCH /payments/10/` `{}` | `400` `{"error": "No fields to update"}` |
| `PATCH /payments/10/` `{"amount":"-1"}` | `400` `{"error": "Validation failed", "fields": {"amount": "amount must be greater than 0"}}` |
| `PATCH /payments/9999/` | `404` `{"error": "Payment not found"}` |
| `DELETE /payments/10/` | `405 Method Not Allowed` (`Allow: GET, PATCH`) |