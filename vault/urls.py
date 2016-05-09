from django.conf.urls import url
from . import views


app_name = 'vault'

urlpatterns = [
    url(r'^$', views.login_view, name='login_view'),
    url(r'vault$', views.find_vault, name='find_vault'),
    url(r'^auth_view$', views.auth_view, name='auth_view'),
    url(r'^create_user_view', views.create_user_view, name='create_user_view'),
    url(r'^logout', views.logout_view, name='logout'),
    ]
