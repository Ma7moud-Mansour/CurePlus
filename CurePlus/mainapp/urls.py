from django.urls import path

from mainapp import views


urlpatterns = [
    path("", views.home, name="home"),
    path("payment/webhook/", views.paymob_webhook, name="paymob_webhook"),
    path("payment/callback/", views.paymob_callback, name="paymob_callback"),
]
