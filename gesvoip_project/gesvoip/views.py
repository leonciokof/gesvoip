from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse_lazy
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.views import generic

from . import forms, models


class LazyEncoder(DjangoJSONEncoder):

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class cpanelView(generic.TemplateView):

    """ Vista de cpanel """

    template_name = 'gesvoip/cpanel.html'

cpanel = cpanelView.as_view()


class cpanel_gesvoipView(generic.TemplateView):

    """ Vista de cpanel_gesvoip """

    template_name = 'gesvoip/cpanel_gesvoip.html'

cpanel_gesvoip = cpanel_gesvoipView.as_view()


class ingresa_userView(generic.CreateView):

    """ Vista de ingresa_user """

    form_class = forms.UsuariosForm
    model = models.Usuarios
    template_name = 'gesvoip/ingresa_user.html'
    success_url = reverse_lazy('gesvoip:listar_user')

ingresa_user = ingresa_userView.as_view()


class busca_userView(generic.FormView):

    """ Vista de busca_user """

    form_class = forms.BuscaUserForm
    template_name = 'gesvoip/busca_user.html'

    def get_context_data(self, **kwargs):
        context = super(busca_userView, self).get_context_data(**kwargs)
        context.update({'object_list': models.Usuarios.objects.all()})

        return context

    def form_valid(self, form):
        self.usuario = form.cleaned_data.get('usuario')

        return super(busca_userView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'gesvoip:modifica_user', kwargs={'pk': self.usuario.id_usuario})

busca_user = busca_userView.as_view()


class modifica_userView(generic.UpdateView):

    """ Vista de modifica_user """

    form_class = forms.UsuariosForm
    model = models.Usuarios
    success_url = reverse_lazy('gesvoip:listar_user')
    template_name = 'gesvoip/modifica_user.html'

modifica_user = modifica_userView.as_view()


class listar_userView(generic.TemplateView):

    """ Vista de listar_user """

    template_name = 'gesvoip/listar_user.html'

    def get_context_data(self, **kwargs):
        context = super(listar_userView, self).get_context_data(**kwargs)
        context.update({'object_list': models.Usuarios.objects.all()})

        return context

listar_user = listar_userView.as_view()


class ingresa_companiaView(generic.TemplateView):

    """ Vista de ingresa_compania """

    template_name = 'gesvoip/ingresa_compania.html'

ingresa_compania = ingresa_companiaView.as_view()


class busca_companiaView(generic.FormView):

    """ Vista de busca_compania """

    form_class = forms.BuscaCompaniaForm
    template_name = 'gesvoip/busca_compania.html'

    def get_context_data(self, **kwargs):
        context = super(busca_companiaView, self).get_context_data(**kwargs)
        context.update({'object_list': models.Compania.objects.all()})

        return context

    def form_valid(self, form):
        self.compania = form.cleaned_data.get('compania')

        return super(busca_companiaView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'gesvoip:modifica_compania',
            kwargs={'pk': self.compania.id_compania})

busca_compania = busca_companiaView.as_view()


class modifica_companiaView(generic.UpdateView):

    """ Vista de modifica_compania """

    form_class = forms.CompaniaForm
    model = models.Compania
    template_name = 'gesvoip/modifica_compania.html'

modifica_compania = modifica_companiaView.as_view()


class listar_companiaView(generic.TemplateView):

    """ Vista de listar_compania """

    template_name = 'gesvoip/listar_compania.html'

listar_compania = listar_companiaView.as_view()


class ingresa_tarifaView(generic.FormView):

    """ Vista de ingresa_tarifa """

    form_class = forms.NuevaTarifaForm
    success_url = reverse_lazy('gesvoip:ingresa_tarifa')
    template_name = 'gesvoip/ingresa_tarifa.html'

    def form_valid(self, form):
        compania = form.cleaned_data.get('compania')
        fecha_inicio = form.cleaned_data.get('fecha_inicio')
        fecha_fin = form.cleaned_data.get('fecha_fin')
        valor_normal = form.cleaned_data.get('valor_normal')
        valor_reducido = form.cleaned_data.get('valor_reducido')
        valor_nocturno = form.cleaned_data.get('valor_nocturno')

        if fecha_fin < fecha_inicio:
            return self.form_invalid(form)

        models.Tarifa.ingress(
            compania, fecha_inicio, fecha_fin, valor_normal, valor_reducido,
            valor_nocturno)

        return super(ingresa_tarifaView, self).form_valid(form)

ingresa_tarifa = ingresa_tarifaView.as_view()


class busca_tarifaView(generic.FormView):

    """ Vista de busca_tarifa """

    form_class = forms.CompaniaFechaForm
    template_name = 'gesvoip/busca_tarifa.html'

    def form_valid(self, form):
        self.compania = form.cleaned_data.get('compania')
        self.year = form.cleaned_data.get('year')
        self.month = form.cleaned_data.get('month')

        return super(busca_tarifaView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'gesvoip:listar_tarifa',
            kwargs={
                'compania': self.compania.pk, 'year': self.year,
                'month': self.month})

busca_tarifa = busca_tarifaView.as_view()


class busca_tarifa2View(generic.FormView):

    """ Vista de busca_tarifa2 """

    form_class = forms.CompaniaFechaForm
    template_name = 'gesvoip/busca_tarifa2.html'

    def form_valid(self, form):
        self.compania = form.cleaned_data.get('compania')
        self.year = form.cleaned_data.get('year')
        self.month = form.cleaned_data.get('month')

        return super(busca_tarifa2View, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'gesvoip:busca_tarifa3',
            kwargs={
                'compania': self.compania.pk, 'year': self.year,
                'month': self.month})

busca_tarifa2 = busca_tarifa2View.as_view()


class busca_tarifa3View(generic.TemplateView):

    """ Vista de busca_tarifa3 """

    template_name = 'gesvoip/busca_tarifa3.html'

    def get_context_data(self, **kwargs):
        context = super(busca_tarifa3View, self).get_context_data(**kwargs)
        object_list = models.Tarifa.get_by_compania_and_fecha(
            kwargs.get('compania'), kwargs.get('year'), kwargs.get('month'))
        context.update({'object_list': object_list})

        return context

busca_tarifa3 = busca_tarifa3View.as_view()


class modifica_tarifaView(generic.FormView):

    """ Vista de modifica_tarifa """

    form_class = forms.EditaTarifaForm
    success_url = reverse_lazy('gesvoip:busca_tarifa2')
    template_name = 'gesvoip/modifica_tarifa.html'

    def form_valid(self, form):
        id_ingreso = form.cleaned_data.get('id_ingreso')
        valor_normal = form.cleaned_data.get('valor_normal')
        valor_reducido = form.cleaned_data.get('valor_reducido')
        valor_nocturno = form.cleaned_data.get('valor_nocturno')

        if 'eliminar' in form.data:
            models.Tarifa.objects.filter(id_ingreso=id_ingreso).delete()

        elif 'modificar' in form.data:
            models.Tarifa.objects.filter(id_ingreso=id_ingreso).update(
                valor_normal=valor_normal, valor_reducido=valor_reducido,
                valor_nocturno=valor_nocturno)

        return super(modifica_tarifaView, self).form_valid(form)

    def get_initial(self):
        tarifa = models.Tarifa.get_by_id_ingreso(self.kwargs.get('pk'))

        return {
            'id_ingreso': tarifa.id_ingreso,
            'valor_normal': tarifa.valor_normal,
            'valor_reducido': tarifa.valor_reducido,
            'valor_nocturno': tarifa.valor_nocturno}

modifica_tarifa = modifica_tarifaView.as_view()


class listar_tarifaView(generic.TemplateView):

    """ Vista de listar_tarifa """

    template_name = 'gesvoip/listar_tarifa.html'

    def get_context_data(self, **kwargs):
        context = super(listar_tarifaView, self).get_context_data(**kwargs)
        tarifas = models.Tarifa.get_by_compania_and_fecha(
            kwargs.get('compania'),
            kwargs.get('year'),
            kwargs.get('month'))
        tarifas = [
            {
                'fecha_inicio': t['fecha_inicio'],
                'fecha_fin': t['fecha_fin'],
                'tarifas': models.Tarifa.objects.filter(
                    id_ingreso=t['id_ingreso'])
            } for t in tarifas]
        context.update({'object_list': tarifas})

        return context

listar_tarifa = listar_tarifaView.as_view()


class ingresa_feriadoView(generic.CreateView):

    """ Vista de ingresa_feriado """

    form_class = forms.FeriadoForm
    model = models.Feriado
    template_name = 'gesvoip/ingresa_feriado.html'

ingresa_feriado = ingresa_feriadoView.as_view()


class eliminar_feriadoView(generic.FormView):

    """ Vista de eliminar_feriado """

    form_class = forms.BuscaFeriadoForm
    template_name = 'gesvoip/eliminar_feriado.html'
    success_url = reverse_lazy('gesvoip:eliminar_feriado')

    def form_valid(self, form):
        feriado = form.cleaned_data.get('feriado')
        feriado.delete()

        return super(eliminar_feriadoView, self).form_valid(form)

eliminar_feriado = eliminar_feriadoView.as_view()


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


class carga_cdrView(generic.CreateView):

    """ Vista de carga_cdr """

    form_class = forms.CdrForm
    model = models.Cdr
    success_url = reverse_lazy('gesvoip:procesar_cdr')
    template_name = 'gesvoip/carga_cdr.html'

carga_cdr = carga_cdrView.as_view()


class procesar_cdrView(generic.FormView):

    """ Vista de procesar_cdr """

    form_class = forms.ProcesaCdrForm
    success_url = reverse_lazy('gesvoip:procesar_cdr')
    template_name = 'gesvoip/procesar_cdr.html'

    def form_valid(self, form):
        result = models.Cdr.processes()
        messages.success(self.request, result)

        return super(procesar_cdrView, self).form_valid(form)

procesar_cdr = procesar_cdrView.as_view()


class consulta_cdrView(generic.TemplateView):

    """ Vista de consulta_cdr """

    template_name = 'gesvoip/consulta_cdr.html'

consulta_cdr = consulta_cdrView.as_view()


class eliminar_cdrView(generic.TemplateView):

    """ Vista de eliminar_cdr """

    template_name = 'gesvoip/eliminar_cdr.html'

eliminar_cdr = eliminar_cdrView.as_view()


class genera_facturaView(generic.CreateView):

    """ Vista de genera_factura """

    form_class = forms.FacturaForm
    model = models.Factura
    success_url = reverse_lazy('gesvoip:genera_factura')
    template_name = 'gesvoip/genera_factura.html'

    def get_success_url(self):
        self.object.facturar()
        return reverse_lazy(
            'gesvoip:modifica_factura', kwargs={'pk': self.object.pk})

genera_factura = genera_facturaView.as_view()


class busca_facturaView(generic.FormView):

    """ Vista de busca_factura """

    form_class = forms.BuscaFacturaForm
    template_name = 'gesvoip/busca_factura.html'

    def get_context_data(self, **kwargs):
        context = super(busca_facturaView, self).get_context_data(**kwargs)
        context.update({'object_list': models.Factura.objects.all()})

        return context

    def form_valid(self, form):
        self.factura = form.cleaned_data.get('factura')
        print(self.factura)

        return super(busca_facturaView, self).form_valid(form)

    def get_success_url(self):
        print(self.factura.pk)
        return reverse_lazy(
            'gesvoip:modifica_factura', kwargs={'pk': self.factura.pk})

busca_factura = busca_facturaView.as_view()


class modifica_facturaView(generic.DetailView):

    """ Vista de modifica_factura """

    model = models.Factura
    template_name = 'gesvoip/modifica_factura.html'

modifica_factura = modifica_facturaView.as_view()


class eliminar_facturaView(generic.FormView):

    """ Vista de eliminar_factura """

    form_class = forms.BuscaFacturaForm
    template_name = 'gesvoip/eliminar_factura.html'
    success_url = reverse_lazy('gesvoip:eliminar_factura')

    def form_valid(self, form):
        factura = form.cleaned_data.get('factura')
        factura.reset_logs()
        factura.delete()

        return super(eliminar_facturaView, self).form_valid(form)

eliminar_factura = eliminar_facturaView.as_view()


class consulta_facturaView(generic.TemplateView):

    """ Vista de consulta_factura """

    template_name = 'gesvoip/consulta_factura.html'

consulta_factura = consulta_facturaView.as_view()


class carga_portadosView(generic.TemplateView):

    """ Vista de carga_portados """

    template_name = 'gesvoip/carga_portados.html'

carga_portados = carga_portadosView.as_view()
