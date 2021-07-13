from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from .forms import  EmailForm
from .models import Receiver, MailingList, Mailing, MailingReceiver
import json
from datetime import date
from django.conf import settings

@csrf_exempt
def emails(request):
    if request.method == 'GET':
        data = Receiver.objects.all()
        data_json = serializers.serialize('json', data)
        return JsonResponse(json.loads(data_json), safe=False)
    elif request.method == 'POST':

        email_req = json.loads(request.body)
        print(email_req["email"], email_req["name"], email_req["surname"], email_req["bday"])

        try:
            new_obj = Receiver.objects.create(email=email_req["email"],
                                name=email_req["name"],
                                surname=email_req["surname"],
                                bday=email_req["bday"])
            new_obj.save()
        except :
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
                new_obj = MailingList(title=mailing_list_req["title"])
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

        if mailing_req.get("pk"):
            try:
                mailing_list = MailingList.objects.get(pk=mailing_req["pk"])
            except:
                pass
        elif mailing_req.get("ml_title"):
            try:
                mailing_list = MailingList.objects.get(title=mailing_req["ml_title"])
            except:
                pass
        else:
            return HttpResponse("Nothing to add")

        if mailing_req.get("mailing_date"):
            mailing_date = mailing_req["mailing_date"]
        else:
            mailing_date = date.today()
        try:
            print(mailing_req["title"], mailing_list, mailing_date)
            new_obj = Mailing.objects.create(
                title=mailing_req["title"],
                mailing_date=mailing_date,
                mailing_list=mailing_list
            )
        except :
            return HttpResponse("something goes wrong")

        return HttpResponse(status=200)


def add_emails(request):
    if request.method == 'GET':
        form = EmailForm()
    elif request.method == 'POST':
        # если метод POST, проверим форму и отправим письмо
        form = EmailForm(request.POST)
        if form.is_valid():
            #"email", "name", "surname", "bday"
            new_obj = Receiver.objects.create(email=request.POST["email"],
                                               name=request.POST["name"],
                                               surname=request.POST["surname"],
                                               bday=request.POST["bday"]
                                               )
            new_obj.save()
            return HttpResponse('Email added')
    else:
        return HttpResponse('Request ERROR')
    return render(request, "emailapp/addemail.html", {'form': form})

'''

def contact_view(request):
    # если метод GET, вернем форму
    if request.method == 'GET':
        form = ContactForm()
    elif request.method == 'POST':
        # если метод POST, проверим форму и отправим письмо
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            try:
                send_mail(f'{subject} от {from_email}', message,
                          settings.DEFAULT_FROM_EMAIL, settings.RECIPIENTS_EMAIL)
            except BadHeaderError:
                return HttpResponse('Ошибка в теме письма.')
            return redirect('success')
    else:
        return HttpResponse('Неверный запрос.')
    return render(request, "email.html", {'form': form})

def success_view(request):
    return HttpResponse('Приняли! Спасибо за вашу заявку.')'''