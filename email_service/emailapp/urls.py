from django.contrib import admin
from django.urls import path

from .views import emails, mailing_list, mailing, templates, active_mailing, open_tracking, emails_edit
from .views import mailing_list_edit, mailing_edit, templates_edit

urlpatterns = [
    path('emails/', emails, name='emails'),
    path('emails/<int:pk>/', emails_edit, name='emails_edit'),
    path('mailing-list/', mailing_list, name='mailing_list'),
    path('mailing-list/<int:pk>/', mailing_list_edit, name='mailing_list'),
    path('mailing/', mailing, name='mailing'),
    path('mailing/<int:pk>/', mailing_edit, name='mailing_edit'),
    path('templates/', templates, name='templates'),
    path('templates/<int:pk>/', templates_edit, name='templates_edit'),
    path('activate-mailing/', active_mailing, name='active_mailing'),
    path("open-tracking/<int:pk>/", open_tracking, name="pixel_view")

]