from email_service.celery import celery_app
from .models import MailingReceiver, Mailing, MailingList, Receiver, HtmlTemplate
from datetime import date
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.utils.html import strip_tags
from django.core import serializers
from django.conf import settings
import json
@celery_app.task
def sending():
    objs = Mailing.objects.filter(mailing_status=False).filter(mailing_date__lte=date.today())
    if objs:
        for mailing in objs:
            mailinglist = MailingList.objects.get(pk=mailing.mailing_list_id)
            emails = mailinglist.receivers.all()
            for receiver in emails:
                obj = MailingReceiver.objects.create(mailing=mailing, receiver=receiver)
                send_email.delay(obj.pk)
            mailing.mailing_status = True
            mailing.save()

@celery_app.task
def send_email(pk):
    obj = MailingReceiver.objects.get(pk=pk)
    receiver = Receiver.objects.get(pk=obj.receiver_id)
    mailing = Mailing.objects.get(pk=obj.mailing_id)

    template_dict = model_to_dict(receiver)
    template = HtmlTemplate.objects.get(pk=mailing.mailing_template_id)
    template_dir = settings.DEFAULT_TEMPLATES_DIR + "/mailing/" + template.template_location
    html_message = render_to_string(template_dir, template_dict)
    html_message = html_message[:html_message.find("</body>")] \
                   + f'<img src="{settings.PROJECT_DOMAIN}/open-tracking/{pk}/">' \
                   + html_message[html_message.find("</body>"):]
    plain_message = strip_tags(html_message)

    subject = mailing.mailing_subject
    from_email = settings.EMAIL_HOST_USER
    to = receiver.email


    send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    obj.send = True

    return subject, plain_message, from_email, to