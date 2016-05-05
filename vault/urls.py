from django.conf.urls import url, include
from . import views
from django.contrib.auth.views import login


app_name = 'vault'

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'vault$', views.find_vault, name='find_vault'),
    url(r'^auth_view$', views.auth_view, name='auth_view'),
    ]
