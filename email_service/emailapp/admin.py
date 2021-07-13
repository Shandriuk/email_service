from django.contrib import admin

# Register your models here.
from .models import  Receiver, MailingList, Mailing, MailingReceiver

admin.site.register(Receiver)
admin.site.register(MailingList)
admin.site.register(Mailing)
admin.site.register(MailingReceiver)