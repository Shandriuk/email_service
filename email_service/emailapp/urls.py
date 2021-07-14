from django.contrib import admin
from django.urls import path, re_path

from .views import   emails, mailing_list, mailing, sending_test, templates, start_mailing, open_tracking

urlpatterns = [
    path('api/emails/', emails, name='emails'),
    path('api/mailing_list/', mailing_list, name='mailing_list'),
    path('api/mailing/', mailing, name='mailing'),
    path('api/sending/', sending_test, name='sending'),
    path('api/templates/', templates, name='templates'),
    path('api/start_mailing/', start_mailing, name='start_mailing'),
    path("open-tracking/<int:pk>/", open_tracking, name="pixel_view")

]