from django.shortcuts import render, redirect
from General.models import Members, Events, ClassLevel
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import Http404
import requests
from requests.auth import HTTPBasicAuth
import os

# Create your views here.

class MailChimpError(Exception): pass

class MailChimp:
    token = "099152d0593d91dfe0becffef63d35dd-us11"
    url = "https://us13.api.mailchimp.com/3.0"
    listID = "53f0c18efe"

    @classmethod
    def AddUserToList(cls, email, firstname, lastname):
        url = os.path.join(cls.url, "lists/{0}/members/".format(cls.listID))
        data = dict(
            email_address=email,
            merge_fields=dict(
                FNAME=firstname,
                LNAME=lastname
            ),
            status="subscribed"
        )
        auth = HTTPBasicAuth('anystring', cls.token)
        res = requests.post(url, auth=auth, json=data)
        if res.status_code >= 200 or res.status_code <= 399 :
            return res.json()
        raise MailChimpError("Failed with status code: {0}".format(res.status_code))

def index(request):
    context = dict()
    Events.RetrieveFromFB()
    context["events"] = {
        "current": Events.CurrentEvents(),
        "expired": Events.ExpiredEvents()
    }
    context["team"] = Members.getAllEboard()
    return render(request, "General/index.html", context=context)

@login_required
def getCode(request, event=None):
    if event is None:
        events = Events.GetOpenEvents()
        return render(request, "General/codeList.html", {"events":events, "url":"/getEventCode/"})
    event = Events.objects.get(fb_id=event)
    if event.code is None:
        event.generateCode()
        pass
    return render(request, "General/codeDisplay.html", {"event":event})

@login_required
def closeEvent(request, event):
    event = Events.objects.get(fb_id=event)
    event.closed = True
    event.save()
    return redirect("/getEventCode")

@csrf_protect
def loginForEvent(request):
    if request.method == 'GET':
        return render(request, "General/eventCheckin.html")
    if request.method == 'POST':
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")
        user = Members.objects.filter(email=email).first()
        if user is None:
            return redirect("/check-in/new/{0}?email={1}".format(code, email))
        event = Events.GetEventFromCode(code)
        if event is None:
            raise Http404
        user.events.add(event)
        user.save()
        return redirect("/check-in/good/{0}".format(code))

@csrf_protect
def goodCheckin(request, code):
    event = Events.GetEventFromCode(code)
    if event is None:
        raise Http404
    return render(request, "General/good.html", {"event":event})

@csrf_protect
def newCheckin(request, code):
    event = Events.GetEventFromCode(code)
    if event is None:
        raise Http404
    if request.method == 'GET':
        email = request.GET.get("email", "")
        levels = ClassLevel.objects.all()
        return render(request, "General/new.html", {"event": event, "email": email, "levels": levels})
    if request.method == "POST":
        email = request.POST.get("email", "")
        name = request.POST.get("name", "")
        clsLevel = request.POST.get("level", "")
        clsLevel = ClassLevel.objects.get(id=clsLevel)
        user = Members(email=email, name=name, level=clsLevel)
        namesplit = name.split(" ")
        lastname = namesplit[-1] if len(namesplit) >= 2 else None
        MailChimp.AddUserToList(email=email, firstname=namesplit[0], lastname=lastname)
        user.save()
        user.events.add(event)
        user.save()
        return redirect("/check-in/good/{0}".format(code))

@login_required
def getAttendees(request, event=None):
    if event is None:
        events = Events.GetOpenEvents()
        return render(request, "General/codeList.html", {"events":events, "url":"/events/"})
    event = Events.objects.get(fb_id=event)
    users = event.members_set.all()
    return render(request, "General/attendeeList.html", {"users":users, "count": len(users), "event": event})

def getEligible(request, vote_run):
    if vote_run not in {"vote", "run"}:
        raise Http404
    mems = []
    if vote_run == "vote":
        mems = Members.getEligible(vote=True)
    else:
        mems = Members.getEligible()
        pass
    return render(request, "General/eligible.html", {"users": mems, "action": vote_run})
