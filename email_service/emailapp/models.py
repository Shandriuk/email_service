from django.db import models

# Create your models here.


class Receiver(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=20, blank=True)
    surname = models.CharField(max_length=20, blank=True)
    bday = models.DateField(auto_now=False, blank=True)

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email


class MailingList(models.Model):
    title = models.CharField(max_length=30, blank=True, unique=True)
    receivers = models.ManyToManyField(Receiver)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Mailing(models.Model):
    title =models.CharField(max_length=30, blank=True, unique=True)
    mailing_list = models.ForeignKey(MailingList, null=True,  on_delete=models.SET_NULL)
    mailing_date = models.DateField(auto_now=True)
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class MailingReceiver(models.Model):
    mailing = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    send = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    send_date = models.DateField()
    received_date = models.DateField()