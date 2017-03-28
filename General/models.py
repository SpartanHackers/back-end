from django.db import models
from django.db.models import Count
import datetime
import requests
import dateutil.parser
import string
import random

from datetime import timezone

def utc_to_local(utc_dt):
    return utc_dt.astimezone(tz=timezone.utc)

# Create your models here.

class ClassLevel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    pass

def rowObject(query, size=3):
    totalData = []
    row = []
    for i in query:
        row.append(i)
        if len(row) == size:
            totalData.append(row)
            row = []
            pass
        pass
    totalData.append(row)
    return totalData

class Events(models.Model):
    name = models.TextField()
    time = models.DateTimeField(db_index=True)
    location = models.TextField(null=True, blank=True)
    information = models.TextField()
    fb_id = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=6, null=True, unique=True, db_index=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return "{0}:{1}".format(self.name, self.url)

    @classmethod
    def GenerateCode(cls, size=6, chars=string.ascii_letters+string.digits):
        code = "".join((random.choice(chars) for _ in range(size)))
        if cls.GetEventFromCode(code):
            return cls.GenerateCode(size=size, chars=chars)
        return code

    def generateCode(self, *args, **kwargs):
        self.code = Events.GenerateCode(*args, **kwargs)
        self.save()
        pass

    @classmethod
    def GetOpenEvents(cls):
        return cls.objects.filter(closed=False)

    @classmethod
    def RetrieveFromFB(cls, url=None, app_token=None):
        if url is None:
            url = "https://graph.facebook.com/v2.6/1530644923816171/events"
        if app_token is None:
            params = {
                "client_id": 1011811655559043,
                "client_secret": "e142cf5f7d119fa678981f125b9a49a6",
                "grant_type": "client_credentials"
            }
            app_token = requests.get("https://graph.facebook.com/oauth/access_token", params=params).text.split("=")[-1]
            pass
        params = {
            "key": "value",
            "access_token": app_token
        }
        data = requests.get(url, params).json()
        events = data["data"]
        for event in events:
            if cls.objects.filter(fb_id=event["id"]).first() is not None:
                continue
            time = event["start_time"].replace("-0400", "+0000")
            time = dateutil.parser.parse(time)
            time = utc_to_local(time)
            location = event.get("place")
            if location is None:
                location = ""
                pass
            else:
                location = location.get("name", "1345 Engineering Building")
                pass
            obj = dict(
                name=event["name"],
                location=location,
                information=event.get("description", "Description coming soon"),
                fb_id=event["id"],
                time=time,
            )
            newEvent = cls(**obj)
            newEvent.save()
            newEvent.generateCode()
            pass

        nex_url = data["paging"].get("next")
        if nex_url is not None:
            return cls.RetrieveFromFB(nex_url, app_token)
        pass

    @classmethod
    def GetEventFromCode(cls, code):
        return cls.objects.filter(code=code).filter(closed=False).first()

    class Meta:
        ordering = ("-time", )
        pass

    def getAllUsers(self):
        return self.members_set

    @property
    def url(self):
        return "https://www.facebook.com/events/{0}/".format(self.fb_id)

    @classmethod
    def CurrentEvents(cls):
        return rowObject(cls.objects.filter(time__gte=datetime.datetime.now()))

    @classmethod
    def ExpiredEvents(cls):
        return rowObject(cls.objects.filter(time__lt=datetime.datetime.now()))

    pass
class Interest(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    pass

class Members(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    level = models.ForeignKey(ClassLevel)
    is_eboard = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    events = models.ManyToManyField(Events, blank=True)
    interests = models.ManyToManyField(Interest, null=True, blank=True)
    picture = models.ImageField(blank=True, null=True, )

    def __str__(self):
        return "{0}:{1}".format(self.name, self.email)

    def signin(self, event):
        self.events.add(event)
        pass

    @classmethod
    def getEligible(cls, vote=False):
        requiredCount = 4
        if vote:
            requiredCount = 2
            pass
        return cls.objects.annotate(c=Count("events")).filter(c__gte=requiredCount)

    @classmethod
    def getAllEboard(cls):
        return rowObject(cls.objects.filter(is_eboard=True))

    @classmethod
    def getAllEmails(cls):
        return cls.objects.values_list("email", flat=True)

    pass
