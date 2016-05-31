from django.conf.urls import url
from . import views

"""
URL patterns used by 'spierdon' app.
"""
urlpatterns = [
    url(r'^aisite/new', views.create, name='create'),
    url(r'^aisite/match/(?P<match_id>[0-9]+)/update', views.update_match, name='update_match'),
    url(r'^aisite/(?P<aisite_id>[0-9]+)/detail/force=(?P<force>[0-9]+)', views.detail, name='force_detail'),
    url(r'^aisite/(?P<aisite_id>[0-9]+)/detail', views.detail, name='detail'),
    url(r'^aisite/(?P<aisite_id>[0-9]+)/join', views.join, name='join'),
    url(r'^aisite/(?P<aisite_id>[0-9]+)/edit', views.edit, name='edit'),
    # url(r'^challenges/', views.get_challenges, name='get_challenges'),
    url(r'^', views.index, name='index'),
]
