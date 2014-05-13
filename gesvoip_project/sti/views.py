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
