from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles import views

from .views import new_status, status, boost, reply, follow
from .views import home_tl, user_notif, user_tl, tag_tl

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^web/statuses/new', new_status, name="new_status"),
    url(r'^web/statuses/([0-9]+)/boost', boost, name="boost"),
    url(r'^web/statuses/([0-9]+)/reply', reply, name="reply"),
    url(r'^web/statuses/([0-9]+)', status, name="status"),

    url(r'^web/notifications', user_notif, name="user_notif"),
    url(r'^web/timelines/home', home_tl, name="home_tl"),
    url(r'^web/timelines/tag/(\w+)', tag_tl, name="tag_tl"),

    url(r'^admin/', admin.site.urls),

    url(r'static/(.+)', views.serve),

    url(r'^@([^/]+)', user_tl, name="user_tl"),
    url(r'^@([^/]+)/follow', follow, name="follow"),
]
