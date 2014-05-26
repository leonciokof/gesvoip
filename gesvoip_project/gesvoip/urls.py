from django.conf.urls import patterns, url

urlpatterns = patterns(
    'gesvoip.views',
    url(r'^new_cdr/$', 'new_cdr', name='new_cdr'),
    url(r'^new_rate/$', 'new_rate', name='new_rate'),
    url(r'^incoming_list/$', 'incoming_list', name='incoming_list'),
    url(r'^invoice_list/$', 'invoice_list', name='invoice_list'),
    url(r'^company_list/$', 'company_list', name='company_list'),
    url(r'^company_create/$', 'company_create', name='company_create'),
    url(r'^company_update/(?P<pk>\w+)/$',
        'company_update', name='company_update'),
    url(r'^invoice_datail/(?P<pk>\w+)/$',
        'invoice_datail', name='invoice_datail'),
    url(r'^holiday_list/$', 'holiday_list', name='holiday_list'),
    url(r'^holiday_create/$', 'holiday_create', name='holiday_create'),
    url(r'^holiday_update/(?P<pk>\w+)/$',
        'holiday_update', name='holiday_update'),
    url(r'^numeration_list/(?P<pk>\w+)/$',
        'numeration_list', name='numeration_list'),
)
