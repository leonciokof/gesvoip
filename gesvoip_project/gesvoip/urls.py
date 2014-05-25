from django.conf.urls import patterns, url

urlpatterns = patterns(
    'gesvoip.views',
    url(r'^new_cdr/$', 'new_cdr', name='new_cdr'),
    url(r'^new_rate/$', 'new_rate', name='new_rate'),
    url(r'^incoming_list/$', 'incoming_list', name='incoming_list'),
    url(r'^invoice_list/$', 'invoice_list', name='invoice_list'),
    url(r'^company_list/$', 'company_list', name='company_list'),
    url(r'^company_update/(?P<pk>\w+)/$',
        'company_update', name='company_update'),
    url(r'^period_list/(?P<pk>\w+)/$', 'period_list', name='period_list'),
    url(r'^rate_list/(?P<pk>\w+)/$', 'rate_list', name='rate_list'),
    url(r'^invoice_resumen/(?P<pk>\w+)/$',
        'invoice_resumen', name='invoice_resumen'),
)
