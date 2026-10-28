from django.shortcuts import render, get_object_or_404
from .models import Payment

def payment_list(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'payments_app/payment_list.html', {
        'payments': payments
    })

def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments_app/payment_detail.html', {
        'payment': payment
    })
