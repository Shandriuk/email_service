import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.utils import IntegrityError

import re
import pytz
from os import path
from .models import Receiver, MailingList, Mailing, MailingReceiver, HtmlTemplate
import json
from datetime import date, datetime
from django.conf import settings
from .tasks import sending
from urllib import parse
from django.forms.models import model_to_dict
from django.db.models import Q

# regexes for checking dates and emails
regex_date = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])$'
regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


@csrf_exempt
def emails(request):

    if request.method == 'GET':
        # method get and query string searching
        qs = request.META["QUERY_STRING"]
        if qs == "":
            # request with no Query String
            data = Receiver.objects.all().order_by('-id')[:50]
            data_json = [model_to_dict(elem) for elem in data]

            return JsonResponse({"status": "success", "results": data_json})
        else:
            # request with  Query String
            qs_dict = dict(parse.parse_qsl(qs))

            if qs_dict.get("email"):
                # mail searching
                email = qs_dict.get("email")
                data = Receiver.objects.filter(Q(email__icontains=email))

                data_json = [model_to_dict(elem) for elem in data]
                if data_json:
                    return JsonResponse({"status": "success", "results": data_json})
                return JsonResponse({"status": "fail", "description": "nothing found"})
            return JsonResponse({"status": "fail", "description": "please provide email in querystring"})


    elif request.method == 'POST':
        # method post
        email_req = json.loads(request.body)

        # correct email checking
        if not (re.match(regex_email, email_req.get("email"))):
            return JsonResponse({"status": "fail", "description": "please provide correct email"})
        # if date provided, check it
        if email_req.get("bday") and not (re.match(regex_date, email_req.get("bday"))):
            return JsonResponse({"status": "fail", "description": "please provide correct correct date"})

        try:
            new_mail = Receiver.objects.create(
                            email=email_req.get("email"),
                            name=email_req.get("name") if email_req.get("name") else "",
                            lastname=email_req.get("lastname") if email_req.get("lastname") else "",
                            bday=email_req.get("bday") if email_req.get("bday") else None)
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique email"})

        return JsonResponse({"status": "success", "description": "you added new email", "result": model_to_dict(new_mail)})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST)"})

@csrf_exempt
def emails_edit(request, pk=None):
    try:
        receiver = Receiver.objects.get(pk=pk)
    except Receiver.DoesNotExist:
        return JsonResponse({"status": "fail", "description": "please provide correct pk"})

    if request.method == 'GET':
        return JsonResponse({"status": "success", "results": model_to_dict(receiver)})

    elif request.method == 'POST':
        # method post
        email_req = json.loads(request.body)

        # checking and adding new email
        receiver.email = email_req.get("email") \
            if email_req.get("email") and (re.match(regex_email, email_req.get("email"))) else receiver.email
        try:
            receiver.save()
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique email"})
        # adding new name and lastname
        receiver.name = email_req.get("name") if email_req.get("name") else receiver.name
        receiver.lastname = email_req.get("lastname") if email_req.get("lastname") else receiver.lastname
        # chaecking and adding new bday
        receiver.bday = email_req.get("bday")\
            if email_req.get("bday") and (re.match(regex_date, email_req.get("bday"))) else receiver.bday

        receiver.save()

        return JsonResponse({"status": "success", "results": model_to_dict(receiver), "description": "you edited email"})


    elif request.method == 'DELETE':
        # method delete
        receiver.delete()
        return JsonResponse({"status": "success", "description": "you deleted email"})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST, DELETE)"})


@csrf_exempt
def mailing_list(request):
    if request.method == 'GET':
        # method get and query string searching
        qs = request.META["QUERY_STRING"]
        if qs == "":
            data = MailingList.objects.all().order_by('-id')[:50]
            data_json=[]
            for mailing_list in data:
                receivers=[]
                for email in mailing_list.receivers.all():
                    receivers.append(email.pk)
                data_json.append({"mailinglist_name":mailing_list.mailinglist_name, "receivers":receivers})
            #data_json = [model_to_dict(elem) for elem in data]
            return JsonResponse({"status": "success", "results": data_json})
        else:
            qs_dict = dict(parse.parse_qsl(qs))
            # mailinglist_name searching
            if qs_dict.get("mailinglist_name"):
                mailinglist_name = qs_dict.get("mailinglist_name")
                data = MailingList.objects.filter(Q(mailinglist_name__icontains=mailinglist_name))
                # output json serializing
                data_json = []
                for mailing_list in data:
                    receivers = []
                    for email in mailing_list.receivers.all():
                        receivers.append(email.id)
                    data_json.append({"mailinglist_name": mailing_list.mailinglist_name, "receivers": receivers})

                if data_json:
                    return JsonResponse({"status": "success", "results": data_json})
                return JsonResponse({"status": "fail", "description": "nothing found"})
            return JsonResponse({"status": "fail", "description": "please provide mailinglist_name in query string"})

    elif request.method == 'POST':

        mailing_list_req = json.loads(request.body)
        adding_emails = []
        failure_adding = []

        # adding emails
        if mailing_list_req.get("emails_pk"):
            for pk in mailing_list_req["emails_pk"]:
                try:
                    adding_emails.append(Receiver.objects.get(pk=pk))
                except Receiver.DoesNotExist:
                    failure_adding.append(pk)

        if mailing_list_req.get("emails"):
            if isinstance(mailing_list_req.get("emails"), list):
                for email in mailing_list_req["emails"]:
                    adding_emails.append(Receiver.objects.get_or_create(email=email)[0])
            elif isinstance(mailing_list_req.get("emails"), str):
                adding_emails.append(Receiver.objects.get_or_create(email=mailing_list_req["emails"])[0])
        # checking if emails in adding list
        if len(adding_emails) != 0:
            try:
                new_mailing_list = MailingList(mailinglist_name=mailing_list_req.get("mailinglist_name"))
                new_mailing_list.save()
                for elem in adding_emails:
                    new_mailing_list.receivers.add(elem)
            except IntegrityError:
                return JsonResponse({"status": "fail", "description": "please provide unique mailinglist_name"})
        else:
            return JsonResponse({"status": "fail", "description": "nothing to add"})

        # output json serializing
        receivers = []
        for email in new_mailing_list.receivers.all():
            receivers.append(email.id)
        data_json = {"mailinglist_name": new_mailing_list.mailinglist_name, "receivers": receivers}

        if len(failure_adding) == 0:
            return JsonResponse({"status": "success", "description": "you added new mailing list", "result":data_json})
        else:
            return JsonResponse({"status": "partial success",
                                 "description": f"you added new mailing list {data_json}, but some email pks don`t added",
                                 "failure_pks": failure_adding})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST)"})

@csrf_exempt
def mailing_list_edit(request, pk=None):
    try:
        mailinglist = MailingList.objects.get(pk=pk)
    except MailingList.DoesNotExist:
        return JsonResponse({"status": "fail", "description": "please provide correct pk"})

    if request.method == 'GET':
        # get mailing list with id =  request pk
        receivers = []
        for email in mailinglist.receivers.all():
            receivers.append(email.id)
        data_json = {"mailinglist_name": mailinglist.mailinglist_name, "receivers": receivers}
        return JsonResponse({"status": "success", "results": data_json})
    elif request.method == 'POST':

        ml_req = json.loads(request.body)

        ml_name = ml_req.get("mailinglist_name")

        mailinglist.mailinglist_name = ml_name if ml_name else mailinglist.mailinglist_name
        # adding emails command
        receiver_failed = []
        if ml_req.get("receivers_add") and isinstance(ml_req.get("receivers_add"), list):
            receivers_list = ml_req.get("receivers_add")
            for receiver in receivers_list:
                try:
                    mailinglist.receivers.add(receiver)
                except:
                    receiver_failed.append(receiver)

        # removing emails command
        if ml_req.get("receivers_remove") and isinstance(ml_req.get("receivers_pop"), list):
            receivers_list = ml_req.get("receivers_pop")
            for receiver in receivers_list:
                try:
                    mailinglist.receivers.remove(receiver)
                except:
                    pass
        try:
            mailinglist.save()
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique mailinglist_name"})
        # output json serializing
        receivers = []
        for email in mailinglist.receivers.all():
            receivers.append(email.id)
        data_json = {"mailinglist_name": mailinglist.mailinglist_name, "receivers": receivers}

        if len(receiver_failed) > 0:
            return JsonResponse({"status": "success", "results": data_json, "description": f"you edited mailinglist, but failed adding some emails {receiver_failed}"})
        return JsonResponse({"status": "success", "results": data_json, "description": "you edited mailinglist"})

    elif request.method == 'DELETE':
        mailinglist.delete()
        return JsonResponse({"status": "success", "description": "you deleted mailinglist"})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST, DELETE)"})


@csrf_exempt
def mailing(request):
    # method GET
    if request.method == 'GET':
        qs = request.META["QUERY_STRING"]
        if qs == "":
            data = Mailing.objects.all().order_by('-id')[:50]
            data_json = [model_to_dict(elem) for elem in data]
            return JsonResponse({"status": "success", "results": data_json})
        else:
            qs_dict = dict(parse.parse_qsl(qs))
            # mailinglist_name searching
            if qs_dict.get("mailing_name"):
                mailing_name = qs_dict.get("mailing_name")
                data = Mailing.objects.filter(Q(mailing_name__icontains=mailing_name))

                data_json = [model_to_dict(elem) for elem in data]
                if data_json:
                    return JsonResponse({"status": "success", "results": data_json})
                return JsonResponse({"status": "fail", "description": "nothing found"})
    # method POST
    elif request.method == 'POST':
        mailing_req = json.loads(request.body)

        # checking mailing_list
        if mailing_req.get("mailing_list") or mailing_req.get("mailing_list_name"):
            if mailing_req.get("mailing_list"):
                try:
                    m_list = MailingList.objects.get(pk=mailing_req["mailing_list"])
                except MailingList.DoesNotExist:
                    return JsonResponse({"status": "fail", "description": "Please provide correct mailing_list"})
            else:
                try:
                    m_list = MailingList.objects.get(mailinglist_name=mailing_req["mailing_list_name"])
                except:
                    return JsonResponse({"status": "fail", "description": "Please provide correct mailing_list_name"})
        else:
            return JsonResponse({"status": "fail", "description": "Please add mailing_list or mailing_list_name fields"})

        # checking mailing_template
        if mailing_req.get("mailing_template") or mailing_req.get("mailing_template_name"):
            if mailing_req.get("mailing_template"):
                try:
                    mailing_template = HtmlTemplate.objects.get(pk=mailing_req["mailing_template"])
                except HtmlTemplate.DoesNotExist:
                    return JsonResponse({"status": "fail", "description": "Please provide correct mailing_template"})
            else:
                try:
                    mailing_template = HtmlTemplate.objects.get(template_name=mailing_req["mailing_template_name"])
                except HtmlTemplate.DoesNotExist:
                    return JsonResponse({"status": "fail", "description": "Please provide correct mailing_template_name"})
        else:
            return JsonResponse({"status": "fail", "description": "Please add mailing_template or mailing_template_name fields"})

        # checking date
        if mailing_req.get("mailing_date") and not (re.match(regex_date, mailing_req.get("mailing_date"))):
            return JsonResponse({"status": "fail", "description": "please provide correct date YYYY-MM-DD"})

        if not mailing_req.get("mailing_name"):
            return JsonResponse({"status": "fail", "description": "please provide unique mailing_name"})

        try:
            new_mailing = Mailing.objects.create(
                mailing_name=mailing_req["mailing_name"],
                mailing_date=mailing_req.get("mailing_date") if mailing_req.get("mailing_date") else date.today(),
                mailing_list=m_list,
                mailing_subject=mailing_req.get("subject") if mailing_req.get("subject") else "",
                mailing_body=mailing_req.get("body") if mailing_req.get("body") else "",
                mailing_signature=mailing_req.get("signature") if mailing_req.get("signature") else "",
                mailing_template=mailing_template
            )
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique mailing_name"})

        return JsonResponse({"status": "success", "description": "you added new mailing", "result": model_to_dict(new_mailing)})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST)"})

@csrf_exempt
def mailing_edit(request, pk=None):
    try:
        mlng = Mailing.objects.get(pk=pk)
    except Mailing.DoesNotExist:
        return JsonResponse({"status": "fail", "description": "please provide correct pk"})

    if request.method == 'GET':

        if mlng.mailing_status:
            # is status True adding sent email info
            mlng_json = model_to_dict(mlng)

            m_r = MailingReceiver.objects.filter(mailing_id=mlng.id)
            result_of_mailing = []
            for mails in m_r:
                result_of_mailing.append(model_to_dict(mails))
            mlng_json.update({"mailing_result":result_of_mailing})

            return JsonResponse({"status": "success", "results": mlng_json})
        return JsonResponse({"status": "success", "results": model_to_dict(mlng)})
    elif request.method == 'POST':
        mln_req = json.loads(request.body)
        try:
            mlng.mailing_name = mln_req.get("mailing_name") if mln_req.get("mailing_name") else mlng.mailing_name
            mlng.save()
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique mailing_name"})

        if mln_req.get("mailing_date"):
            if re.match(regex_date, mln_req.get("mailing_date")):
                mlng.mailing_date = mln_req.get("mailing_date")
        # changing mailing status
        mlng.mailing_status = False if mln_req.get("mailing_status") == "False" else \
            True if mln_req.get("mailing_status") == "True" else mlng.mailing_status

        # changing subject, body, signature=
        mlng.mailing_subject =mln_req.get("mailing_subject") if mln_req.get("mailing_subject")\
                              else mlng.mailing_subject
        mlng.mailing_body = mln_req.get("mailing_body") if mln_req.get("mailing_body")\
                              else mlng.mailing_body
        mlng.mailing_signature=mln_req.get("mailing_signature") if mln_req.get("mailing_signature")\
                              else mlng.mailing_signature
        mlng.save()

        #mailing list changing
        if mln_req.get("mailing_list"):
            try:
                ml = MailingList.objects.get(pk=mln_req.get("mailing_list"))
            except MailingList.DoesNotExist:
                return JsonResponse({"status": "fail", "description": "please provide correct mailing_list"})
            mlng.mailing_list = ml
            mlng.save()

        # HtmlTemplate list changing
        if mln_req.get("mailing_template"):
            try:
                ht = HtmlTemplate.objects.get(pk=mln_req.get("mailing_template"))
            except HtmlTemplate.DoesNotExist:
                return JsonResponse({"status": "fail", "description": "please provide correct mailing_template pk"})
            mlng.mailing_template = ht
            mlng.save()

        return JsonResponse({"status": "success", "results": model_to_dict(mlng), "description": "you edited mailing"})

    elif request.method == 'DELETE':
        mlng.delete()
        return JsonResponse({"status": "success", "description": "you deleted mailing"})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST, DELETE)"})


@csrf_exempt
def activate_mailing(request):
    if request.method == 'GET':
        active_mailing = Mailing.objects.filter(mailing_status=False).order_by('-id')[:50]
        data_json = [model_to_dict(elem) for elem in active_mailing]
        return JsonResponse({"status": "success", "results": data_json})
    elif request.method == 'POST':
        active_mailing = Mailing.objects.filter(mailing_status=False).filter(mailing_date__lte=date.today())
        if len(active_mailing) > 0:
            sending.delay()
            return JsonResponse({"status": "success", "description": "you started all accessible mailing"})
        else:
            return JsonResponse({"status": "success", "description": "no accessible mailing to start"})

@csrf_exempt
def templates(request):
    if request.method == 'GET':
        active_mailing = HtmlTemplate.objects.all().order_by('-id')[:50]
        data_json = [model_to_dict(elem) for elem in active_mailing]
        return JsonResponse({"status": "success", "results": data_json}, safe=False)
    elif request.method == 'POST':
        template_req = json.loads(request.body)

        if template_req.get("template_location") and template_req.get("template_name"):
            # checking template_location
            if not path.exists(settings.DEFAULT_TEMPLATES_DIR + "/mailing/" + template_req["template_location"]):
                return JsonResponse({"status": "fail",
                                     "description": "Please provide correct template_location that exist in template/mailing folder"})

            try:
                new_ht = HtmlTemplate.objects.create(
                    template_location=template_req["template_location"],
                    template_name=template_req["template_name"]
                )
            except IntegrityError:
                return JsonResponse({"status": "fail",
                                     "description": "Please provide unique template_name"})
            return JsonResponse({"status": "success", "description": "you added template", "result":model_to_dict(new_ht)})

        else:
            return JsonResponse({"status": "fail",
                                 "description": "Please provide correct template_location and template_name"})

@csrf_exempt
def templates_edit(request, pk=None):
    try:
        ht = HtmlTemplate.objects.get(pk=pk)
    except HtmlTemplate.DoesNotExist:
        return JsonResponse({"status": "fail", "description": "please provide correct pk"})
    if request.method == 'GET':
        return JsonResponse({"status": "success", "results": model_to_dict(ht)})
    elif request.method == 'POST':
        ht_req = json.loads(request.body)
        # changing template_name
        try:
            ht.template_name = ht_req.get("template_name") if ht_req.get("template_name") else ht.template_name
            ht.save()
        except IntegrityError:
            return JsonResponse({"status": "fail", "description": "please provide unique template_name"})

        # checking and changing template_location
        if ht_req.get("template_location") and path.exists(settings.DEFAULT_TEMPLATES_DIR + "/mailing/" + ht_req.get("template_location")):
            ht.mailing_signature = ht_req.get("template_location")
            ht.save()

        return JsonResponse(
                {"status": "success", "results": model_to_dict(ht), "description": "you edited mailing"})
    elif request.method == 'DELETE':
        ht.delete()
        return JsonResponse({"status": "success", "description": "you deleted mailing"})
    else:
        return JsonResponse({"status": "fail", "description": "please provide correct method(GET, POST, DELETE)"})


def open_tracking(request, pk=None):
    image_data = open(path.join(settings.BASE_DIR, 'static/img/open-tracking/pixel.png'), 'rb').read()
    try:
        mr_obj = MailingReceiver.objects.get(pk=pk)
        if not mr_obj.received:
            mr_obj.received = True
            mr_obj.received_date = datetime.now(tz=pytz.UTC)
            mr_obj.save()
    except MailingReceiver.DoesNotExist:
        pass

    return HttpResponse(image_data, content_type="image/png")
