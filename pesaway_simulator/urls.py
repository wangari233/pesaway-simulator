from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/payments/', include('payments_app.urls')),
    path('payments/', include('payments_app.api_urls')),
]
