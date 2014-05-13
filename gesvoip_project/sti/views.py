from django.core.urlresolvers import reverse_lazy
from django.views import generic

from . import forms, models


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
