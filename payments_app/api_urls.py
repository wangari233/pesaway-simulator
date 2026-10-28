from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.payment_list, name='api_payment_list'),
    path('<int:pk>/', api_views.payment_detail, name='api_payment_detail'),
]