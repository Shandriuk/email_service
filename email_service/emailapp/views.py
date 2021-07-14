import datetime

from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

import pytz
from os import path
from .models import Receiver, MailingList, Mailing, MailingReceiver, HtmlTemplate
import json
from datetime import date, datetime
from django.conf import settings
from .tasks import send_email, sending


@csrf_exempt
def emails(request):
    if request.method == 'GET':
        data = Receiver.objects.all()
        data_json = serializers.serialize('json', data)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':

        email_req = json.loads(request.body)

        try:
            new_obj = Receiver.objects.create(email=email_req["email"],
                                name=email_req["name"],
                                lastname=email_req["lastname"],
                                bday=email_req["bday"])
            new_obj.save()
        except ZeroDivisionError:
            return HttpResponse("something goes wrong")

        return HttpResponse(status=200)

@csrf_exempt
def mailing_list(request):
    if request.method == 'GET':
        data = MailingList.objects.all()
        data_json = serializers.serialize('json', data)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':

        mailing_list_req = json.loads(request.body)
        adding_emails = []
        if mailing_list_req.get("pks"):
            for pk in mailing_list_req["pks"]:
                try:
                    adding_emails.append(Receiver.objects.get(pk=pk))
                except:
                    pass
        if mailing_list_req.get("emails"):
            for email in mailing_list_req["emails"]:
                try:
                    adding_emails.append(Receiver.objects.get(email=email))
                except:
                    Receiver.objects.create(email=email)
        if len(adding_emails)!=0:
            try:
                new_obj = MailingList(mailinglist_name=mailing_list_req["mailinglist_name"])
                new_obj.save()
                for elem in adding_emails:
                    new_obj.receivers.add(elem)
            except:
                return HttpResponse("something goes wrong")
        else:
            return HttpResponse("Nothing to add")
        return HttpResponse(status=200)

@csrf_exempt
def mailing(request):
    if request.method == 'GET':
        data = Mailing.objects.all()
        data_json = serializers.serialize('json', data)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':
        mailing_req = json.loads(request.body)

        if mailing_req.get("ml_pk") or mailing_req.get("ml_name"):
            if mailing_req.get("ml_pk"):
                try:
                    mailing_list = MailingList.objects.get(pk=mailing_req["ml_pk"])
                except:
                    pass
            else:
                try:
                    mailing_list = MailingList.objects.get(mailinglist_name=mailing_req["ml_name"])
                except:
                    pass
        else:
            return HttpResponse("Please add ml_pk or ml_name fields")

        if mailing_req.get("ht_pk") or mailing_req.get("ht_name"):
            if mailing_req.get("ht_pk"):
                try:
                    mailing_template = HtmlTemplate.objects.get(pk=mailing_req["ht_pk"])
                except:
                    pass
            else:
                try:
                    mailing_template = HtmlTemplate.objects.get(template_name=mailing_req["ht_name"])
                except:
                    pass
        else:
            return HttpResponse("Please add ht_pk or ht_name fields")

        if mailing_req.get("mailing_date"):
            mailing_date = mailing_req["mailing_date"]
        else:
            mailing_date = date.today()
        try:
            #print(mailing_req["title"], mailing_list, mailing_date)
            new_obj = Mailing.objects.create(
                mailing_name=mailing_req["mailing_name"],
                mailing_date=mailing_date,
                mailing_list=mailing_list,
                mailing_subject=mailing_req["subject"],
                mailing_template=mailing_template
            )
        except :
            return HttpResponse("something goes wrong")

        return HttpResponse(status=200)


@csrf_exempt
def start_mailing(request):
    if request.method == 'GET':
        active_mailing = Mailing.objects.filter(mailing_status=True)
        data_json = serializers.serialize('json', active_mailing)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':
        sending.delay()
        return HttpResponse('You start all needed mailing')

@csrf_exempt
def templates(request):
    if request.method == 'GET':
        active_mailing = HtmlTemplate.objects.all()
        data_json = serializers.serialize('json', active_mailing)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':
        template_req = json.loads(request.body)
        if template_req.get("template_location") and template_req.get("template_name"):
            try:
                HtmlTemplate.objects.create(
                    template_location=template_req["template_location"],
                    template_name=template_req["template_name"]
                )
            except:
                return HttpResponse("something goes wrong")
            return HttpResponse(status=200)
        else:
            return HttpResponse('Nothing to add')



def open_tracking(request, pk=None):

    image_data = open(path.join(settings.BASE_DIR, 'static/img/open-tracking/pixel.png'), 'rb').read()
    mr_obj = MailingReceiver.objects.get(pk=pk)
    if mr_obj.received == False:
        mr_obj.received=True
        mr_obj.received_date=datetime.now(tz=pytz.UTC)
        mr_obj.save()

    return HttpResponse(image_data, content_type="image/png")