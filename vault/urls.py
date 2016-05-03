from django.conf.urls import url
from . import views


app_name = 'vault'

urlpatterns = [
    url(r'^$', views.login, name='login'),
    ]