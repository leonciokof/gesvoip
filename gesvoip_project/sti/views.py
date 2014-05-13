import csv

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
