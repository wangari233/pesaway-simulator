from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = "SUCCESS", "Success"
        FAILED = 'FAILED', 'Failed'

    class Currency(models.TextChoices):
        KES = "KES", "Kenyan Shilling"
        UGX = "UGX", "Ugandan Shilling"

    class PaymentMethod(models.TextChoices):
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        BANK = "BANK", "Bank"    

    reference = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique transaction reference ID"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    currency = models.CharField(
        max_length=3, 
        choices=Currency.choices
    )
    phone_number = models.CharField(max_length=15)
    payment_method = models.CharField(
    max_length=20,
    choices=PaymentMethod.choices
)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="payment_amount_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency} ({self.status})"





