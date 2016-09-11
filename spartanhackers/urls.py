"""spartanhackers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from django.contrib import admin
from General.views import index, getCode, closeEvent, loginForEvent, goodCheckin, newCheckin, getAttendees, getEligible
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index, name="index"),
    url(r'^index$', index, name="index"),
    url(r'^index.html$', index, name="index"),
    url(r'^getEventCode/$', getCode, name="getCode"),
    url(r'^getEventCode/(?P<event>.*)/close$', closeEvent, name="closeEvent"),
    url(r'^getEventCode/(?P<event>.*)$', getCode, name="getCode"),
    url(r'^check-in/good/(?P<code>.*)$', goodCheckin, name="good"),
    url(r'^check-in/new/(?P<code>.*)$', newCheckin, name="new"),
    url(r'^check-in/$', loginForEvent, name="checkin"),
    url(r'^events/$', getAttendees, name="allAttendees"),
    url(r'^events/(?P<event>.*)$', getAttendees, name="event_attendees"),
    url(r'^members/eligible/(?P<vote_run>.*)$', getEligible, name="event_attendees"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
