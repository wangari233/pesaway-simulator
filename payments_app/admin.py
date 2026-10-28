from django.contrib import admin
from payments_app.models import  Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "amount", "currency", "status", "created_at")