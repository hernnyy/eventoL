from django.conf.urls import url
from event import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
]
