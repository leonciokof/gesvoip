from django.conf.urls import patterns, url

urlpatterns = patterns(
    'sti.views',
    url(r'^cpanel_sti/$', 'cpanel_sti', name='cpanel_sti'),
    url(r'^sti_locales/$', 'sti_locales', name='sti_locales'),
    url(r'^sti_locales2/$', 'sti_locales2', name='sti_locales2'),
    url(r'^sti_locales3/(?P<pk>\d+)/$', 'sti_locales3', name='sti_locales3'),
    url(r'^sti_informe_locales/$',
        'sti_informe_locales', name='sti_informe_locales'),
    url(r'^sti_informe_locales2/(?P<year>\d+)/(?P<month>\d+)/$',
        'sti_informe_locales2', name='sti_informe_locales2'),
)
