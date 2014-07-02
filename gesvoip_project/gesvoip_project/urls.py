from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^', include('gesvoip.urls', namespace='gesvoip')),
    url(r'^', include('sti.urls', namespace='sti')),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)
