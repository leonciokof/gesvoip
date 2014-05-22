from django.core.urlresolvers import reverse_lazy
from django.views import generic

from . import forms, models, tasks


class NewRateView(generic.FormView):

    """ Vista de new_rate """

    form_class = forms.RateForm
    success_url = reverse_lazy('gesvoip:new_rate')
    template_name = 'gesvoip/new_rate.html'

    def form_valid(self, form):
        company = form.cleaned_data.get('company')
        year = form.cleaned_data.get('year')
        month = form.cleaned_data.get('month')
        normal_price = form.cleaned_data.get('normal_price')
        reduced_price = form.cleaned_data.get('reduced_price')
        nightly_price = form.cleaned_data.get('nightly_price')
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        i = models.Invoice.objects.filter(
            company=company, month=month, year=year).first()

        if i is None:
            i = models.Invoice(company=company, month=month, year=year).save()

        p = models.Period(invoice=i, start=start, end=end).save()
        models.Rate(period=p, _type='normal', price=normal_price).save()
        models.Rate(period=p, _type='reducido', price=reduced_price).save()
        models.Rate(period=p, _type='nocturno', price=nightly_price).save()

        return super(NewRateView, self).form_valid(form)

new_rate = NewRateView.as_view()


class NewCdrView(generic.FormView):

    """ Vista de new_cdr """

    form_class = forms.CdrForm
    success_url = reverse_lazy('gesvoip:new_cdr')
    template_name = 'gesvoip/new_cdr.html'

    def form_valid(self, form):
        year = form.cleaned_data.get('year')
        month = form.cleaned_data.get('month')
        incoming_entel = form.cleaned_data.get('incoming_entel')
        incoming_ctc = form.cleaned_data.get('incoming_ctc')
        outgoing = form.cleaned_data.get('outgoing')

        cdr = models.Cdr(
            year=year, month=month, incoming_entel=incoming_entel,
            incoming_ctc=incoming_ctc, outgoing=outgoing).save()
        tasks.insert_incoming.delay(cdr)

        return super(NewCdrView, self).form_valid(form)

new_cdr = NewCdrView.as_view()
