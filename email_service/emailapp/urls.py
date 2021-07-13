from django.contrib import admin
from django.urls import path

from .views import  add_emails, emails, mailing_list, mailing

urlpatterns = [
    path('addemails/', add_emails, name='addemails'),
    path('api/emails/', emails, name='emails'),
    path('api/mailing_list/', mailing_list, name='mailing_list'),
    path('api/mailing/', mailing, name='mailing'),
]