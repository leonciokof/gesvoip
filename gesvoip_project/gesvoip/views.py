from django.contrib.auth.models import User
from django.views import generic

from . import forms, models


class cpanel_gesvoipView(generic.TemplateView):

    """ Vista de cpanel_gesvoip """

    template_name = 'gesvoip/cpanel_gesvoip.html'

cpanel_gesvoip = cpanel_gesvoipView.as_view()


class ingresa_userView(generic.CreateView):

    """ Vista de ingresa_user """

    form_class = forms.UsuariosForm
    model = models.Usuarios
    template_name = 'gesvoip/ingresa_user.html'

ingresa_user = ingresa_userView.as_view()


class busca_userView(generic.TemplateView):

    """ Vista de busca_user """

    template_name = 'gesvoip/busca_user.html'

    def get_context_data(self, **kwargs):
        context = super(busca_userView, self).get_context_data(**kwargs)
        context.update({'users': User.objects.all()})

        return context

busca_user = busca_userView.as_view()


class modifica_userView(generic.TemplateView):

    """ Vista de modifica_user """

    template_name = 'gesvoip/modifica_user.html'

modifica_user = modifica_userView.as_view()


class listar_userView(generic.TemplateView):

    """ Vista de listar_user """

    template_name = 'gesvoip/listar_user.html'

listar_user = listar_userView.as_view()


class ingresa_companiaView(generic.TemplateView):

    """ Vista de ingresa_compania """

    template_name = 'gesvoip/ingresa_compania.html'

ingresa_compania = ingresa_companiaView.as_view()


class busca_companiaView(generic.TemplateView):

    """ Vista de busca_compania """

    template_name = 'gesvoip/busca_compania.html'

busca_compania = busca_companiaView.as_view()


class modifica_companiaView(generic.TemplateView):

    """ Vista de modifica_compania """

    template_name = 'gesvoip/modifica_compania.html'

modifica_compania = modifica_companiaView.as_view()


class listar_companiaView(generic.TemplateView):

    """ Vista de listar_compania """

    template_name = 'gesvoip/listar_compania.html'

listar_compania = listar_companiaView.as_view()


class ingresa_tarifaView(generic.TemplateView):

    """ Vista de ingresa_tarifa """

    template_name = 'gesvoip/ingresa_tarifa.html'

ingresa_tarifa = ingresa_tarifaView.as_view()


class busca_tarifaView(generic.TemplateView):

    """ Vista de busca_tarifa """

    template_name = 'gesvoip/busca_tarifa.html'

busca_tarifa = busca_tarifaView.as_view()


class busca_tarifa2View(generic.TemplateView):

    """ Vista de busca_tarifa2 """

    template_name = 'gesvoip/busca_tarifa2.html'

busca_tarifa2 = busca_tarifa2View.as_view()


class busca_tarifa3View(generic.TemplateView):

    """ Vista de busca_tarifa3 """

    template_name = 'gesvoip/busca_tarifa3.html'

busca_tarifa3 = busca_tarifa3View.as_view()


class modifica_tarifaView(generic.TemplateView):

    """ Vista de modifica_tarifa """

    template_name = 'gesvoip/modifica_tarifa.html'

modifica_tarifa = modifica_tarifaView.as_view()


class listar_tarifaView(generic.TemplateView):

    """ Vista de listar_tarifa """

    template_name = 'gesvoip/listar_tarifa.html'

listar_tarifa = listar_tarifaView.as_view()


class ingresa_feriadoView(generic.TemplateView):

    """ Vista de ingresa_feriado """

    template_name = 'gesvoip/ingresa_feriado.html'

ingresa_feriado = ingresa_feriadoView.as_view()


class modifica_feriadoView(generic.TemplateView):

    """ Vista de modifica_feriado """

    template_name = 'gesvoip/modifica_feriado.html'

modifica_feriado = modifica_feriadoView.as_view()


class carga_numeracionView(generic.TemplateView):

    """ Vista de carga_numeracion """

    template_name = 'gesvoip/carga_numeracion.html'

carga_numeracion = carga_numeracionView.as_view()


class procesar_numeracionView(generic.TemplateView):

    """ Vista de procesar_numeracion """

    template_name = 'gesvoip/procesar_numeracion.html'

procesar_numeracion = procesar_numeracionView.as_view()


class busca_numeracionView(generic.TemplateView):

    """ Vista de busca_numeracion """

    template_name = 'gesvoip/busca_numeracion.html'

busca_numeracion = busca_numeracionView.as_view()


class modifica_numeracionView(generic.TemplateView):

    """ Vista de modifica_numeracion """

    template_name = 'gesvoip/modifica_numeracion.html'

modifica_numeracion = modifica_numeracionView.as_view()


class consulta_numeracionView(generic.TemplateView):

    """ Vista de consulta_numeracion """

    template_name = 'gesvoip/consulta_numeracion.html'

consulta_numeracion = consulta_numeracionView.as_view()


class carga_cdrView(generic.TemplateView):

    """ Vista de carga_cdr """

    template_name = 'gesvoip/carga_cdr.html'

carga_cdr = carga_cdrView.as_view()


class procesar_cdrView(generic.TemplateView):

    """ Vista de procesar_cdr """

    template_name = 'gesvoip/procesar_cdr.html'

procesar_cdr = procesar_cdrView.as_view()


class consulta_cdrView(generic.TemplateView):

    """ Vista de consulta_cdr """

    template_name = 'gesvoip/consulta_cdr.html'

consulta_cdr = consulta_cdrView.as_view()


class eliminar_cdrView(generic.TemplateView):

    """ Vista de eliminar_cdr """

    template_name = 'gesvoip/eliminar_cdr.html'

eliminar_cdr = eliminar_cdrView.as_view()


class genera_facturaView(generic.TemplateView):

    """ Vista de genera_factura """

    template_name = 'gesvoip/genera_factura.html'

genera_factura = genera_facturaView.as_view()


class busca_facturaView(generic.TemplateView):

    """ Vista de busca_factura """

    template_name = 'gesvoip/busca_factura.html'

busca_factura = busca_facturaView.as_view()


class modifica_facturaView(generic.TemplateView):

    """ Vista de modifica_factura """

    template_name = 'gesvoip/modifica_factura.html'

modifica_factura = modifica_facturaView.as_view()


class eliminar_facturaView(generic.TemplateView):

    """ Vista de eliminar_factura """

    template_name = 'gesvoip/eliminar_factura.html'

eliminar_factura = eliminar_facturaView.as_view()


class consulta_facturaView(generic.TemplateView):

    """ Vista de consulta_factura """

    template_name = 'gesvoip/consulta_factura.html'

consulta_factura = consulta_facturaView.as_view()


class carga_portadosView(generic.TemplateView):

    """ Vista de carga_portados """

    template_name = 'gesvoip/carga_portados.html'

carga_portados = carga_portadosView.as_view()
