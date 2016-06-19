
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^', include('contest.urls', namespace='contest'), name='main'),
]
