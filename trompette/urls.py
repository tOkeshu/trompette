from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles import views

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^admin/', admin.site.urls),

    url(r'static/(.+)', views.serve),
]
