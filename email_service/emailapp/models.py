from django.db import models
from datetime import datetime, date

# Create your models here.


class Receiver(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=20, blank=True)
    lastname = models.CharField(max_length=20, blank=True)
    bday = models.DateField(auto_now=False, blank=True, null=True)

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

class HtmlTemplate(models.Model):
    template_location = models.CharField(max_length=30)
    template_name = models.CharField(max_length=30, unique=True)

class MailingList(models.Model):
    mailinglist_name = models.CharField(max_length=30, unique=True)
    receivers = models.ManyToManyField(Receiver)

    class Meta:
        ordering = ['mailinglist_name']

    def __str__(self):
        return self.mailinglist_name


class Mailing(models.Model):
    mailing_name = models.CharField(max_length=30, unique=True)
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    mailing_date = models.DateField()
    mailing_status = models.BooleanField(default=False)
    mailing_subject = models.CharField(max_length=30, default="")
    mailing_body = models.TextField(default="", blank=True)
    mailing_signature = models.TextField(default="", blank=True)
    mailing_template = models.ForeignKey(HtmlTemplate,  on_delete=models.CASCADE)
    class Meta:
        ordering = ['mailing_name']

    def __str__(self):
        return self.mailing_name


class MailingReceiver(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    send = models.BooleanField(default=True)
    send_date = models.DateTimeField(auto_now=True)
    received = models.BooleanField(default=False)
    received_date = models.DateTimeField(blank=True, null=True)

