from django.conf.urls import patterns, url

urlpatterns = patterns(
    'gesvoip.views',
    url(r'^$', 'cpanel', name='cpanel'),
    url(r'^cpanel_gesvoip/$', 'cpanel_gesvoip', name='cpanel_gesvoip'),
    url(r'^ingresa_user/$', 'ingresa_user', name='ingresa_user'),
    url(r'^busca_user/$', 'busca_user', name='busca_user'),
    url(r'^modifica_user/(?P<pk>\d+)/$',
        'modifica_user', name='modifica_user'),
    url(r'^listar_user/$', 'listar_user', name='listar_user'),
    url(r'^ingresa_compania/$', 'ingresa_compania', name='ingresa_compania'),
    url(r'^busca_compania/$', 'busca_compania', name='busca_compania'),
    url(r'^modifica_compania/(?P<pk>\d+)/$',
        'modifica_compania', name='modifica_compania'),
    url(r'^listar_compania/$', 'listar_compania', name='listar_compania'),
    url(r'^ingresa_tarifa/$', 'ingresa_tarifa', name='ingresa_tarifa'),
    url(r'^busca_tarifa/$', 'busca_tarifa', name='busca_tarifa'),
    url(r'^busca_tarifa2/$', 'busca_tarifa2', name='busca_tarifa2'),
    url(r'^busca_tarifa3/(?P<compania>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',
        'busca_tarifa3', name='busca_tarifa3'),
    url(r'^modifica_tarifa/(?P<pk>\d+)/$',
        'modifica_tarifa', name='modifica_tarifa'),
    url(r'^listar_tarifa/(?P<compania>\d+)/(?P<year>\d+)/(?P<month>\d+)/$',
        'listar_tarifa', name='listar_tarifa'),
    url(r'^ingresa_feriado/$', 'ingresa_feriado', name='ingresa_feriado'),
    url(r'^eliminar_feriado/$', 'eliminar_feriado', name='eliminar_feriado'),
    url(r'^carga_numeracion/$', 'carga_numeracion', name='carga_numeracion'),
    url(r'^procesar_numeracion/$',
        'procesar_numeracion', name='procesar_numeracion'),
    url(r'^busca_numeracion/$',
        'busca_numeracion', name='busca_numeracion'),
    url(r'^modifica_numeracion/$',
        'modifica_numeracion', name='modifica_numeracion'),
    url(r'^consulta_numeracion/$',
        'consulta_numeracion', name='consulta_numeracion'),
    url(r'^carga_cdr/$', 'carga_cdr', name='carga_cdr'),
    url(r'^procesar_cdr/$', 'procesar_cdr', name='procesar_cdr'),
    url(r'^consulta_cdr/$', 'consulta_cdr', name='consulta_cdr'),
    url(r'^eliminar_cdr/$', 'eliminar_cdr', name='eliminar_cdr'),
    url(r'^genera_factura/$', 'genera_factura', name='genera_factura'),
    url(r'^busca_factura/$', 'busca_factura', name='busca_factura'),
    url(r'^modifica_factura/(?P<pk>\d+)/$',
        'modifica_factura', name='modifica_factura'),
    url(r'^eliminar_factura/$', 'eliminar_factura', name='eliminar_factura'),
    url(r'^consulta_factura/$', 'consulta_factura', name='consulta_factura'),
    url(r'^carga_portados/$', 'carga_portados', name='carga_portados'),
)
