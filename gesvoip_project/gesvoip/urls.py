from django.conf.urls import patterns, url

urlpatterns = patterns(
    'gesvoip.views',
    url(r'^new_cdr/$', 'new_cdr', name='new_cdr'),
)
