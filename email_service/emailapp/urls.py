from django.contrib import admin
from django.urls import path, re_path

from .views import   emails, mailing_list, mailing, templates, start_mailing, open_tracking

urlpatterns = [
    path('emails/', emails, name='emails'),
    path('mailing_list/', mailing_list, name='mailing_list'),
    path('mailing/', mailing, name='mailing'),
    path('templates/', templates, name='templates'),
    path('start_mailing/', start_mailing, name='start_mailing'),
    path("open-tracking/<int:pk>/", open_tracking, name="pixel_view")

]