import csv

from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views import generic

from . import forms, models


class CSVResponseMixin(object):

    def render_to_response(self, context, **response_kwargs):
        r = HttpResponse(content_type='text/csv')
        r['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            context['title'])
        writer = csv.writer(
            r, delimiter=';', lineterminator='\n', dialect='excel')

        for item in context['items']:
            writer.writerow(item)

        return r


class cpanel_stiView(generic.TemplateView):

    """ Vista de cpanel_sti """

    template_name = 'sti/cpanel_sti.html'

cpanel_sti = cpanel_stiView.as_view()


class sti_localesView(generic.CreateView):

    """ Vista de sti_locales """

    form_class = forms.CentrosLocalesForm
    initial = {'cod_empresa': '314'}
    model = models.CentrosLocales
    success_url = reverse_lazy('sti:sti_locales2')
    template_name = 'sti/sti_locales.html'

sti_locales = sti_localesView.as_view()


class sti_locales2View(generic.TemplateView):

    """ Vista de sti_locales2 """

    template_name = 'sti/sti_locales2.html'

    def get_context_data(self, **kwargs):
        context = super(sti_locales2View, self).get_context_data(**kwargs)
        context.update({'object_list': models.CentrosLocales.objects.all()})

        return context

sti_locales2 = sti_locales2View.as_view()


class sti_locales3View(generic.UpdateView):

    """ Vista de sti_locales3 """

    form_class = forms.UpdateCentrosLocalesForm
    model = models.CentrosLocales
    success_url = reverse_lazy('sti:sti_locales2')
    template_name = 'sti/sti_locales3.html'

sti_locales3 = sti_locales3View.as_view()


class sti_informe_localesView(generic.FormView):

    """ Vista de sti_informe_locales """

    form_class = forms.FechaForm
    template_name = 'sti/sti_informe_locales.html'

    def form_valid(self, form):
        self.year = form.cleaned_data.get('year')
        self.month = form.cleaned_data.get('month')

        return super(sti_informe_localesView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'sti:sti_informe_locales2',
            kwargs={'year': self.year, 'month': self.month})

sti_informe_locales = sti_informe_localesView.as_view()


class sti_informe_locales2View(CSVResponseMixin, generic.TemplateView):

    """ Vista de sti_informe_locales2 """

    template_name = 'sti/sti_informe_locales2.html'

    def get_context_data(self, **kwargs):
        context = super(
            sti_informe_locales2View, self).get_context_data(**kwargs)
        fecha = '{0}{1}'.format(kwargs.get('year'), kwargs.get('month'))
        title = 'TL_314_{0}_CL.txt'.format(fecha)
        items = [
            [i.cod_empresa, fecha, i.cod_centro_local, i.desp_centro_local]
            for i in models.CentrosLocales.objects.all()
        ]
        context.update({'title': title, 'items': items})

        return context

sti_informe_locales2 = sti_informe_locales2View.as_view()


class sti_lineasView(generic.FormView):

    """ Vista de sti_lineas """

    form_class = forms.DatoForm
    template_name = 'sti/sti_lineas.html'

sti_lineas = sti_lineasView.as_view()


class sti_lineas2View(generic.TemplateView):

    """ Vista de sti_lineas2 """

    template_name = 'sti/sti_lineas2.html'

    def get_context_data(self, **kwargs):
        context = super(
            sti_lineas2View, self).get_context_data(**kwargs)
        dato = self.request.GET.get('dato', '')
        object_list = models.PnMtc.objects.filter(
            Q(rut_propietario__icontains=dato) |
            Q(numero_telefono__icontains=dato))
        context.update({'object_list': object_list})

        return context

sti_lineas2 = sti_lineas2View.as_view()


class sti_lineas3View(generic.UpdateView):

    """ Vista de sti_lineas3 """

    form_class = forms.PnMtcForm
    model = models.PnMtc
    success_url = reverse_lazy('sti:sti_lineas')
    template_name = 'sti/sti_lineas3.html'

sti_lineas3 = sti_lineas3View.as_view()


class sti_lineas4View(generic.UpdateView):

    """ Vista de sti_lineas4 """

    form_class = forms.LineasForm
    model = models.Lineas
    success_url = reverse_lazy('sti:sti_lineas')
    template_name = 'sti/sti_lineas4.html'

sti_lineas4 = sti_lineas4View.as_view()


class sti_informe_lineasView(generic.FormView):

    """ Vista de sti_informe_lineas """

    form_class = forms.FechaForm
    template_name = 'sti/sti_informe_lineas.html'

    def form_valid(self, form):
        self.year = form.cleaned_data.get('year')
        self.month = form.cleaned_data.get('month')

        return super(sti_informe_lineasView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'sti:sti_informe_lineas2',
            kwargs={'year': self.year, 'month': self.month})

sti_informe_lineas = sti_informe_lineasView.as_view()


class sti_informe_lineas2View(CSVResponseMixin, generic.TemplateView):

    """ Vista de sti_informe_lineas2 """

    template_name = 'sti/sti_informe_lineas2.html'

    def get_context_data(self, **kwargs):
        context = super(
            sti_informe_lineas2View, self).get_context_data(**kwargs)
        items = []
        cod_empresa = 314
        local = 1
        fecha = '{0}{1}'.format(kwargs.get('year'), kwargs.get('month'))
        title = 'TL_314_{0}_LS.txt'.format(fecha)
        lineas = models.Lineas.objects.all().distinct('area', 'comuna')

        for l in lineas:
            area = l.area
            comuna = l.comuna
            post_natural = 0
            post_empresa = 0
            pre_natural = 0

            if area == '58':
                zona_primaria = '01'
            elif area == '57':
                zona_primaria = '02'
            elif area == '55':
                zona_primaria = '03'
            elif area == '51' or area == '52'or area == '53':
                zona_primaria = '04'
            elif area == '32' or area == '33' or area == '34' or area == '35':
                zona_primaria = '05'
            elif area == '2':
                zona_primaria = '06'
            elif area == '72':
                zona_primaria = '07'
            elif area == '75' or area == '73' or area == '71':
                zona_primaria = '08'
            elif area == '41' or area == '42' or area == '43':
                zona_primaria = '09'
            elif area == '45':
                zona_primaria = '10'
            elif area == '63' or area == '65' or area == '64':
                zona_primaria = '11'
            elif area == '67':
                zona_primaria = '12'
            elif area == '61':
                zona_primaria = '13'

            lineas2 = models.Lineas.objects.filter(comuna=comuna)

            for l2 in lineas2:
                numero0 = l2.numero
                persona0 = l2.tipo_persona

                # Naturales PostPago  o Prepago
                if persona0 == 'Natural':
                    result1 = models.PnMtc.objects.filter(
                        modalidad=1, numero_telefono=numero0)
                    if result1.count() > 0:
                        post_natural += 1
                    else:
                        pre_natural += 1

                # Empresas PostPago
                if persona0 == 'Empresa':
                    result3 = models.PnMtc.objects.filter(
                        modalidad=1, numero_telefono=numero0)
                    if result3.count() > 0:
                        post_empresa += 1

            # Imprimiendo Resultados
            if post_natural > 0 and comuna != '':
                items.append([
                    cod_empresa, fecha, zona_primaria, area, comuna, local,
                    'TB', 'RE', 'H', 'PA', 'D', '0', post_natural])
            elif pre_natural > 0 and comuna != '':
                items.append([
                    cod_empresa, fecha, zona_primaria, area, comuna, local,
                    'TB', 'CO', 'H', 'PA', 'D', '0', pre_natural])
            elif post_empresa > 0 and comuna != '':
                items.append([
                    cod_empresa, fecha, zona_primaria, area, comuna, local,
                    'TB', 'RE', 'H', 'PP', 'D', '0', post_empresa])
        context.update({'title': title, 'items': items})

        return context

sti_informe_lineas2 = sti_informe_lineas2View.as_view()


class sti_informe_suscriptoresView(generic.FormView):

    """ Vista de sti_informe_suscriptores """

    form_class = forms.FechaForm
    template_name = 'sti/sti_informe_suscriptores.html'

    def form_valid(self, form):
        self.year = form.cleaned_data.get('year')
        self.month = form.cleaned_data.get('month')

        return super(sti_informe_suscriptoresView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'sti:sti_informe_suscriptores2',
            kwargs={'year': self.year, 'month': self.month})

sti_informe_suscriptores = sti_informe_suscriptoresView.as_view()


class sti_informe_suscriptores2View(CSVResponseMixin, generic.TemplateView):

    """ Vista de sti_informe_suscriptores2 """

    template_name = 'sti/sti_informe_suscriptores2.html'

    def get_context_data(self, **kwargs):
        context = super(
            sti_informe_suscriptores2View, self).get_context_data(**kwargs)
        items = []
        fecha = '{0}{1}'.format(kwargs.get('year'), kwargs.get('month'))
        title = 'VI_314_{0}_SUSCRIPTORES.txt'.format(fecha)
        empresa = models.Lineas.objects.filter(
            tipo_persona='Empresa', numero__regex=r'^5644690').count()
        natural = models.Lineas.objects.filter(
            tipo_persona='Natural', numero__regex=r'^5644690').count()

        if natural > 0:
            items.append([314, fecha, 'RE', natural])

        if empresa > 0:
            items.append([314, fecha, 'CO', empresa])

        context.update({'title': title, 'items': items})

        return context

sti_informe_suscriptores2 = sti_informe_suscriptores2View.as_view()


class sti_ingresa_portadoView(generic.FormView):

    """ Vista de sti_ingresa_portado """

    form_class = forms.PortadoForm
    success_url = reverse_lazy('sti:sti_ingresa_portado')
    template_name = 'sti/sti_ingresa_portado.html'

    def form_valid(self, form):
        numero = form.cleaned_data.get('numero')
        models.PnMtc(numero_telefono=numero).save()
        models.Lineas(numero=numero).save()

        return super(sti_ingresa_portadoView, self).form_valid(form)

sti_ingresa_portado = sti_ingresa_portadoView.as_view()


class ingresa_rango_portadosView(generic.FormView):

    """ Vista de ingresa_rango_portados """

    form_class = forms.RangoPortadoForm
    success_url = reverse_lazy('sti:ingresa_rango_portados')
    template_name = 'sti/ingresa_rango_portados.html'

    def form_valid(self, form):
        pnmtc = []
        lineas = []
        rango_inicio = form.cleaned_data.get('rango_inicio')
        rango_fin = form.cleaned_data.get('rango_fin')
        rut = form.cleaned_data.get('rut')
        tipo_servicio = form.cleaned_data.get('tipo_servicio')
        modalidad = form.cleaned_data.get('modalidad')
        deuda = form.cleaned_data.get('deuda')
        documento = form.cleaned_data.get('documento')
        servicio_especial = form.cleaned_data.get('servicio_especial')
        estado = form.cleaned_data.get('estado')
        nombre_cliente = form.cleaned_data.get('nombre_cliente')
        tipo_persona = form.cleaned_data.get('tipo_persona')
        zona_primaria = form.cleaned_data.get('zona_primaria')
        comuna = form.cleaned_data.get('comuna')
        comentarios = form.cleaned_data.get('comentarios')

        if rango_inicio > rango_fin:
            return self.form_invalid(form)

        else:
            for i in range(rango_inicio, rango_fin + 1):
                pnmtc.append(models.PnMtc(
                    rut_propietario=rut,
                    numero_telefono=i,
                    tipo_servicio=tipo_servicio,
                    modalidad=modalidad,
                    deuda_vencida=deuda,
                    estado=estado,
                    id_documento=documento,
                    tipo_servicio_especial=servicio_especial))
                lineas.append(models.Lineas(
                    numero=i,
                    nombre=nombre_cliente,
                    tipo_persona=tipo_persona,
                    comentarios=comentarios,
                    area=zona_primaria,
                    comuna=comuna))

            models.PnMtc.objects.bulk_create(pnmtc)
            models.Lineas.objects.bulk_create(lineas)

        return super(ingresa_rango_portadosView, self).form_valid(form)

ingresa_rango_portados = ingresa_rango_portadosView.as_view()


class sti_ccaaView(generic.CreateView):

    """ Vista de sti_ccaa """

    form_class = forms.CcaaForm
    success_url = reverse_lazy('sti:sti_ccaa')
    template_name = 'sti/sti_ccaa.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        year = form.cleaned_data.get('year')
        month = form.cleaned_data.get('month')
        concecionaria = form.cleaned_data.get('concecionaria')
        self.object.periodo = '{0}{1}'.format(year, month)
        self.object.concecionaria = concecionaria.codigo
        self.object.save()

        return super(sti_ccaaView, self).form_valid(form)

sti_ccaa = sti_ccaaView.as_view()
