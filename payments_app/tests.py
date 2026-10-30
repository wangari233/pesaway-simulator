import json

from django.test import Client, TestCase

from .models import Payment


class PaymentCreateTests(TestCase):
    def post_json(self, payload):
        return self.client.post(
            "/payments/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def valid_payload(self, **overrides):
        payload = {
            "reference": "TXN700",
            "amount": "100.00",
            "currency": "KES",
            "phone_number": "0700000000",
            "payment_method": "MOBILE_MONEY",
        }
        payload.update(overrides)
        return payload

    def test_valid_creation(self):
        response = self.post_json(
            {
                "reference": "TXN100",
                "amount": "250.00",
                "currency": "KES",
                "phone_number": "0700000000",
                "payment_method": "MOBILE_MONEY",
            }
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["status"], "PENDING")
        self.assertEqual(body["reference"], "TXN100")
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(body["phone_number"], "0700000000")
        self.assertEqual(body["payment_method"], "MOBILE_MONEY")

    def test_duplicate_reference_rejected(self):
        payload = {
            "reference": "TXN200",
            "amount": "100.00",
            "currency": "KES",
            "phone_number": "0700000000",
            "payment_method": "BANK",
        }

        first = self.post_json(payload)
        second = self.post_json(payload)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(Payment.objects.filter(reference="TXN200").count(), 1)

    def test_invalid_amount_rejected(self):
        bad_amounts = ["0", "-5", "abc", "10.123", True]

        for bad in bad_amounts:
            with self.subTest(amount=bad):
                response = self.post_json(
                    {"reference": "TXN300", "amount": bad, "currency": "KES"}
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("amount", response.json()["fields"])

        self.assertEqual(Payment.objects.count(), 0)

    def test_invalid_json_rejected(self):
        response = self.client.post(
            "/payments/",
            data='{"reference": "TXN400", "amount": ',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(Payment.objects.count(), 0)

    def test_unknown_id_returns_404(self):
        get_response = self.client.get("/payments/9999/")
        patch_response = self.client.patch(
            "/payments/9999/",
            data=json.dumps({"amount": "50.00"}),
            content_type="application/json",
        )

        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(patch_response.status_code, 404)
        self.assertIn("error", get_response.json())

    def test_status_update_disallowed(self):
        created = self.post_json(
            {
                "reference": "TXN500",
                "amount": "75.00",
                "currency": "KES",
                "phone_number": "0700000000",
                "payment_method": "MOBILE_MONEY",
            }
        )
        payment_id = created.json()["id"]

        response = self.client.patch(
            f"/payments/{payment_id}/",
            data=json.dumps({"status": "SUCCESS"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.status, "PENDING")

    def test_post_without_csrf_token_rejected(self):
        strict_client = Client(enforce_csrf_checks=True)

        response = strict_client.post(
            "/payments/",
            data=json.dumps(
                {"reference": "TXN600", "amount": "10.00", "currency": "KES"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Payment.objects.count(), 0)

    def test_unsupported_currency_rejected(self):
        response = self.post_json(self.valid_payload(currency="USD"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("currency", response.json()["fields"])
        self.assertEqual(Payment.objects.count(), 0)

    def test_missing_phone_number_rejected(self):
        payload = self.valid_payload()
        del payload["phone_number"]

        response = self.post_json(payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("phone_number", response.json()["fields"])
        self.assertEqual(Payment.objects.count(), 0)

    def test_invalid_payment_method_rejected(self):
        response = self.post_json(self.valid_payload(payment_method="CASH"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("payment_method", response.json()["fields"])
        self.assertEqual(Payment.objects.count(), 0)

    def test_patch_unsupported_currency_rejected(self):
        created = self.post_json(self.valid_payload(reference="TXN800"))
        payment_id = created.json()["id"]

        response = self.client.patch(
            f"/payments/{payment_id}/",
            data=json.dumps({"currency": "USD"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("currency", response.json()["fields"])
        self.assertEqual(Payment.objects.get(pk=payment_id).currency, "KES")