from django.conf.urls import patterns, include, url

from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^', include('gesvoip.urls', namespace='gesvoip')),
    url(r'^', include('sti.urls', namespace='sti')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
