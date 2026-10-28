import json

from django.test import TestCase

from .models import Payment


class PaymentCreateTests(TestCase):
    def post_json(self, payload):
        return self.client.post(
            "/payments/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_valid_creation(self):
        response = self.post_json(
            {"reference": "TXN100", "amount": "250.00", "currency": "KES"}
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["status"], "PENDING")
        self.assertEqual(body["reference"], "TXN100")
        self.assertEqual(Payment.objects.count(), 1)

    def test_duplicate_reference_rejected(self):
        payload = {"reference": "TXN200", "amount": "100.00", "currency": "KES"}

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
            {"reference": "TXN500", "amount": "75.00", "currency": "KES"}
        )
        payment_id = created.json()["id"]

        response = self.client.patch(
            f"/payments/{payment_id}/",
            data=json.dumps({"status": "COMPLETED"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.status, "PENDING")        