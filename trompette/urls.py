from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles import views

from .views import new_status, status, boost, reply

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^web/statuses/new', new_status, name="new_status"),
    url(r'^web/statuses/([0-9]+)/boost', boost, name="boost"),
    url(r'^web/statuses/([0-9]+)/reply', reply, name="reply"),
    url(r'^web/statuses/([0-9]+)', status, name="status"),

    url(r'^admin/', admin.site.urls),

    url(r'static/(.+)', views.serve),
]
