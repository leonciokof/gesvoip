import csv
import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic

from mongogeneric import (
    CreateView, DetailView, ListView, UpdateView, DeleteView)
from mongoengine.django.shortcuts import get_document_or_404

from . import forms, models, tasks


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


class IndexView(generic.RedirectView):

    url = reverse_lazy('gesvoip:new_cdr')

index = IndexView.as_view()


class NewRateView(generic.FormView):

    """ Vista de new_rate """

    form_class = forms.RateForm
    success_url = reverse_lazy('gesvoip:new_rate')
    template_name = 'gesvoip/new_rate.html'

    def form_valid(self, form):
        company = form.cleaned_data.get('company')
        normal_price = form.cleaned_data.get('normal_price')
        reduced_price = form.cleaned_data.get('reduced_price')
        nightly_price = form.cleaned_data.get('nightly_price')
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        year = start[:4]
        month = start[5:][:2]
        cdr, created = models.Cdr.objects.get_or_create(month=month, year=year)
        i, created = models.Invoice.objects.get_or_create(
            company=company, cdr=cdr)
        p = models.Period(invoice=i, start=start, end=end).save()
        models.Rate(period=p, _type='normal', price=normal_price).save()
        models.Rate(period=p, _type='reducido', price=reduced_price).save()
        models.Rate(period=p, _type='nocturno', price=nightly_price).save()

        return super(NewRateView, self).form_valid(form)

new_rate = login_required(NewRateView.as_view())


class NewCdrView(generic.FormView):

    """ Vista de new_cdr """

    form_class = forms.CdrForm
    success_url = reverse_lazy('gesvoip:new_cdr')
    template_name = 'gesvoip/new_cdr.html'
    document = models.Cdr

    def form_valid(self, form):
        year = form.cleaned_data.get('year')
        month = form.cleaned_data.get('month')
        entel = form.cleaned_data.get('entel_file')
        ctc = form.cleaned_data.get('ctc_file')
        sti = form.cleaned_data.get('sti_file')
        cdr, created = models.Cdr.objects.get_or_create(month=month, year=year)
        tasks.insert_cdr.delay(str(cdr.id), [entel, ctc], sti)

        return super(NewCdrView, self).form_valid(form)

new_cdr = login_required(NewCdrView.as_view())


class IncomingListView(ListView):

    document = models.Incoming
    paginate_by = 25

incoming_list = login_required(IncomingListView.as_view())


class IncomingByCdrView(ListView):

    document = models.Incoming
    paginate_by = 25

    def get_queryset(self):
        queryset = super(IncomingByCdrView, self).get_queryset()
        cdr = models.Cdr.objects.get(pk=self.kwargs.get('cdr'))
        return queryset.filter(cdr=cdr)

incoming_by_cdr = login_required(IncomingByCdrView.as_view())


class OutgoingByCdrView(ListView):

    document = models.Outgoing
    paginate_by = 25

    def get_queryset(self):
        queryset = super(OutgoingByCdrView, self).get_queryset()
        cdr = models.Cdr.objects.get(pk=self.kwargs.get('cdr'))
        return queryset.filter(cdr=cdr)

outgoing_by_cdr = login_required(OutgoingByCdrView.as_view())


class InvoiceListView(ListView):

    document = models.Invoice
    paginate_by = 25
    queryset = models.Invoice.objects.all().order_by('-year', '-month')

invoice_list = login_required(InvoiceListView.as_view())


class CompanyListView(ListView):

    document = models.Company
    paginate_by = 25

company_list = login_required(CompanyListView.as_view())


class CompanyUpdateView(UpdateView):

    document = models.Company
    form_class = forms.CompanyForm
    success_url = reverse_lazy('gesvoip:company_list')

    def form_valid(self, form):
        bussines_normal_start = form.cleaned_data.get('bussines_normal_start')
        bussines_normal_end = form.cleaned_data.get('bussines_normal_end')
        bussines_reduced_start = form.cleaned_data.get(
            'bussines_reduced_start')
        bussines_reduced_end = form.cleaned_data.get('bussines_reduced_end')
        bussines_nightly_start = form.cleaned_data.get(
            'bussines_nightly_start')
        bussines_nightly_end = form.cleaned_data.get('bussines_nightly_end')
        saturday_normal_start = form.cleaned_data.get('saturday_normal_start')
        saturday_normal_end = form.cleaned_data.get('saturday_normal_end')
        saturday_reduced_start = form.cleaned_data.get(
            'saturday_reduced_start')
        saturday_reduced_end = form.cleaned_data.get('saturday_reduced_end')
        saturday_nightly_start = form.cleaned_data.get(
            'saturday_nightly_start')
        saturday_nightly_end = form.cleaned_data.get('saturday_nightly_end')
        festive_normal_start = form.cleaned_data.get('festive_normal_start')
        festive_normal_end = form.cleaned_data.get('festive_normal_end')
        festive_reduced_start = form.cleaned_data.get('festive_reduced_start')
        festive_reduced_end = form.cleaned_data.get('festive_reduced_end')
        festive_nightly_start = form.cleaned_data.get('festive_nightly_start')
        festive_nightly_end = form.cleaned_data.get('festive_nightly_end')

        if bussines_normal_start and bussines_normal_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'normal': {
                        'start': bussines_normal_start,
                        'end': bussines_normal_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'normal': {
                            'start': bussines_normal_start,
                            'end': bussines_normal_end}}})

        if bussines_reduced_start and bussines_reduced_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'reduced': {
                        'start': bussines_reduced_start,
                        'end': bussines_reduced_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'reduced': {
                            'start': bussines_reduced_start,
                            'end': bussines_reduced_end}}})

        if bussines_nightly_start and bussines_nightly_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'nightly': {
                        'start': bussines_nightly_start,
                        'end': bussines_nightly_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'nightly': {
                            'start': bussines_nightly_start,
                            'end': bussines_nightly_end}}})

        if saturday_normal_start and saturday_normal_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'normal': {
                        'start': saturday_normal_start,
                        'end': saturday_normal_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'normal': {
                            'start': saturday_normal_start,
                            'end': saturday_normal_end}}})

        if saturday_reduced_start and saturday_reduced_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'reduced': {
                        'start': saturday_reduced_start,
                        'end': saturday_reduced_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'reduced': {
                            'start': saturday_reduced_start,
                            'end': saturday_reduced_end}}})

        if saturday_nightly_start and saturday_nightly_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'nightly': {
                        'start': saturday_nightly_start,
                        'end': saturday_nightly_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'nightly': {
                            'start': saturday_nightly_start,
                            'end': saturday_nightly_end}}})

        if festive_normal_start and festive_normal_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'normal': {
                        'start': festive_normal_start,
                        'end': festive_normal_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'normal': {
                            'start': festive_normal_start,
                            'end': festive_normal_end}}})

        if festive_reduced_start and festive_reduced_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'reduced': {
                        'start': festive_reduced_start,
                        'end': festive_reduced_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'reduced': {
                            'start': festive_reduced_start,
                            'end': festive_reduced_end}}})

        if festive_nightly_start and festive_nightly_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'nightly': {
                        'start': festive_nightly_start,
                        'end': festive_nightly_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'nightly': {
                            'start': festive_nightly_start,
                            'end': festive_nightly_end}}})

        self.object.save()

        return super(CompanyUpdateView, self).form_valid(form)

    def get_initial(self):
        initial = super(CompanyUpdateView, self).get_initial()
        initial = initial.copy()
        if self.object.schedules.get('bussines'):
            if self.object.schedules['bussines'].get('normal'):
                initial.update({
                    'bussines_normal_start': self.object.schedules[
                        'bussines']['normal']['start']})
                initial.update({
                    'bussines_normal_end': self.object.schedules[
                        'bussines']['normal']['end']})
            if self.object.schedules['bussines'].get('reduced'):
                initial.update({
                    'bussines_reduced_start': self.object.schedules[
                        'bussines']['reduced']['start']})
                initial.update({
                    'bussines_reduced_end': self.object.schedules[
                        'bussines']['reduced']['end']})
            if self.object.schedules['bussines'].get('nightly'):
                initial.update({
                    'bussines_nightly_start': self.object.schedules[
                        'bussines']['nightly']['start']})
                initial.update({
                    'bussines_nightly_end': self.object.schedules[
                        'bussines']['nightly']['end']})
        if self.object.schedules.get('saturday'):
            if self.object.schedules['saturday'].get('normal'):
                initial.update({
                    'saturday_normal_start': self.object.schedules[
                        'saturday']['normal']['start']})
                initial.update({
                    'saturday_normal_end': self.object.schedules[
                        'saturday']['normal']['end']})
            if self.object.schedules['saturday'].get('reduced'):
                initial.update({
                    'saturday_reduced_start': self.object.schedules[
                        'saturday']['reduced']['start']})
                initial.update({
                    'saturday_reduced_end': self.object.schedules[
                        'saturday']['reduced']['end']})
            if self.object.schedules['saturday'].get('nightly'):
                initial.update({
                    'saturday_nightly_start': self.object.schedules[
                        'saturday']['nightly']['start']})
                initial.update({
                    'saturday_nightly_end': self.object.schedules[
                        'saturday']['nightly']['end']})
        if self.object.schedules.get('festive'):
            if self.object.schedules['festive'].get('normal'):
                initial.update({
                    'festive_normal_start': self.object.schedules[
                        'festive']['normal']['start']})
                initial.update({
                    'festive_normal_end': self.object.schedules[
                        'festive']['normal']['end']})
            if self.object.schedules['festive'].get('reduced'):
                initial.update({
                    'festive_reduced_start': self.object.schedules[
                        'festive']['reduced']['start']})
                initial.update({
                    'festive_reduced_end': self.object.schedules[
                        'festive']['reduced']['end']})
            if self.object.schedules['festive'].get('nightly'):
                initial.update({
                    'festive_nightly_start': self.object.schedules[
                        'festive']['nightly']['start']})
                initial.update({
                    'festive_nightly_end': self.object.schedules[
                        'festive']['nightly']['end']})
        return initial

company_update = login_required(CompanyUpdateView.as_view())


class InvoiceDetailView(DetailView):

    document = models.Invoice

invoice_datail = login_required(InvoiceDetailView.as_view())


class CompanyCreateView(CreateView):

    document = models.Company
    form_class = forms.CompanyForm
    success_url = reverse_lazy('gesvoip:company_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        bussines_normal_start = form.cleaned_data.get('bussines_normal_start')
        bussines_normal_end = form.cleaned_data.get('bussines_normal_end')
        bussines_reduced_start = form.cleaned_data.get(
            'bussines_reduced_start')
        bussines_reduced_end = form.cleaned_data.get('bussines_reduced_end')
        bussines_nightly_start = form.cleaned_data.get(
            'bussines_nightly_start')
        bussines_nightly_end = form.cleaned_data.get('bussines_nightly_end')
        saturday_normal_start = form.cleaned_data.get('saturday_normal_start')
        saturday_normal_end = form.cleaned_data.get('saturday_normal_end')
        saturday_reduced_start = form.cleaned_data.get(
            'saturday_reduced_start')
        saturday_reduced_end = form.cleaned_data.get('saturday_reduced_end')
        saturday_nightly_start = form.cleaned_data.get(
            'saturday_nightly_start')
        saturday_nightly_end = form.cleaned_data.get('saturday_nightly_end')
        festive_normal_start = form.cleaned_data.get('festive_normal_start')
        festive_normal_end = form.cleaned_data.get('festive_normal_end')
        festive_reduced_start = form.cleaned_data.get('festive_reduced_start')
        festive_reduced_end = form.cleaned_data.get('festive_reduced_end')
        festive_nightly_start = form.cleaned_data.get('festive_nightly_start')
        festive_nightly_end = form.cleaned_data.get('festive_nightly_end')

        if bussines_normal_start and bussines_normal_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'normal': {
                        'start': bussines_normal_start,
                        'end': bussines_normal_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'normal': {
                            'start': bussines_normal_start,
                            'end': bussines_normal_end}}})

        if bussines_reduced_start and bussines_reduced_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'reduced': {
                        'start': bussines_reduced_start,
                        'end': bussines_reduced_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'reduced': {
                            'start': bussines_reduced_start,
                            'end': bussines_reduced_end}}})

        if bussines_nightly_start and bussines_nightly_end:
            if self.object.schedules.get('bussines'):
                self.object.schedules.get('bussines').update({
                    'nightly': {
                        'start': bussines_nightly_start,
                        'end': bussines_nightly_end}})

            else:
                self.object.schedules.update({
                    'bussines': {
                        'nightly': {
                            'start': bussines_nightly_start,
                            'end': bussines_nightly_end}}})

        if saturday_normal_start and saturday_normal_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'normal': {
                        'start': saturday_normal_start,
                        'end': saturday_normal_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'normal': {
                            'start': saturday_normal_start,
                            'end': saturday_normal_end}}})

        if saturday_reduced_start and saturday_reduced_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'reduced': {
                        'start': saturday_reduced_start,
                        'end': saturday_reduced_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'reduced': {
                            'start': saturday_reduced_start,
                            'end': saturday_reduced_end}}})

        if saturday_nightly_start and saturday_nightly_end:
            if self.object.schedules.get('saturday'):
                self.object.schedules.get('saturday').update({
                    'nightly': {
                        'start': saturday_nightly_start,
                        'end': saturday_nightly_end}})

            else:
                self.object.schedules.update({
                    'saturday': {
                        'nightly': {
                            'start': saturday_nightly_start,
                            'end': saturday_nightly_end}}})

        if festive_normal_start and festive_normal_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'normal': {
                        'start': festive_normal_start,
                        'end': festive_normal_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'normal': {
                            'start': festive_normal_start,
                            'end': festive_normal_end}}})

        if festive_reduced_start and festive_reduced_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'reduced': {
                        'start': festive_reduced_start,
                        'end': festive_reduced_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'reduced': {
                            'start': festive_reduced_start,
                            'end': festive_reduced_end}}})

        if festive_nightly_start and festive_nightly_end:
            if self.object.schedules.get('festive'):
                self.object.schedules.get('festive').update({
                    'nightly': {
                        'start': festive_nightly_start,
                        'end': festive_nightly_end}})

            else:
                self.object.schedules.update({
                    'festive': {
                        'nightly': {
                            'start': festive_nightly_start,
                            'end': festive_nightly_end}}})

        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

company_create = login_required(CompanyCreateView.as_view())


class HolidayListView(ListView):

    document = models.Holiday
    paginate_by = 25

holiday_list = login_required(HolidayListView.as_view())


class HolidayCreateView(CreateView):

    document = models.Holiday
    form_class = forms.HolidayForm
    success_url = reverse_lazy('gesvoip:holiday_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        date = form.cleaned_data.get('date')
        try:
            self.object.date = dt.datetime.strptime(date, '%Y-%m-%d')
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        except:
            return self.form_invalid(form)

holiday_create = login_required(HolidayCreateView.as_view())


class HolidayUpdateView(UpdateView):

    document = models.Holiday
    form_class = forms.HolidayForm
    success_url = reverse_lazy('gesvoip:holiday_list')

    def form_valid(self, form):
        date = form.cleaned_data.get('date')
        try:
            self.object.date = dt.datetime.strptime(date, '%Y-%m-%d')
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        except:
            return self.form_invalid(form)

    def get_initial(self):
        initial = super(HolidayUpdateView, self).get_initial()
        initial = initial.copy()
        initial.update({'date': self.object.date.strftime('%Y-%m-%d')})

        return initial

holiday_update = login_required(HolidayUpdateView.as_view())


class NumerationListView(ListView):

    document = models.Numeration
    paginate_by = 25

    def get_queryset(self):
        queryset = super(NumerationListView, self).get_queryset()
        company = models.Company.objects.get(pk=self.kwargs.get('pk'))
        return queryset.filter(company=company)

numeration_list = login_required(NumerationListView.as_view())


class IncomingValidListView(ListView):

    document = models.Incoming
    paginate_by = 25

    def get_queryset(self):
        queryset = super(IncomingValidListView, self).get_queryset()
        invoice = models.Invoice.objects.get(pk=self.kwargs.get('pk'))
        return queryset.filter(
            cdr=invoice.cdr, company=invoice.company, invoiced=True)

incoming_valid_list = login_required(IncomingValidListView.as_view())


class LineListView(ListView):

    document = models.Line
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(LineListView, self).get_context_data(**kwargs)
        context.update({'form_date': forms.ReportForm})

        return context

line_list = login_required(LineListView.as_view())


class LineCreateView(CreateView):

    document = models.Line
    form_class = forms.LineForm
    success_url = reverse_lazy('gesvoip:line_list')

line_create = login_required(LineCreateView.as_view())


class LineUpdateView(UpdateView):

    document = models.Line
    success_url = reverse_lazy('gesvoip:line_list')

line_update = login_required(LineUpdateView.as_view())


class LineRangeView(generic.FormView):

    document = models.Line
    form_class = forms.LineRangeForm
    success_url = reverse_lazy('gesvoip:line_list')
    template_name = 'gesvoip/line_form.html'

    def form_valid(self, form):
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        rut = form.cleaned_data.get('rut')
        service = form.cleaned_data.get('service')
        mode = form.cleaned_data.get('mode')
        due = form.cleaned_data.get('due')
        active = form.cleaned_data.get('active')
        document = form.cleaned_data.get('document')
        special_service = form.cleaned_data.get('special_service')
        name = form.cleaned_data.get('name')
        entity = form.cleaned_data.get('entity')
        comments = form.cleaned_data.get('comments')
        zone = form.cleaned_data.get('zone')
        city = form.cleaned_data.get('city')

        if start < end:
            for i in range(start, end + 1):
                l = models.Line(
                    rut=rut,
                    number=i,
                    service=service,
                    mode=mode,
                    due=due,
                    active=active,
                    document=document,
                    name=name,
                    entity=entity,
                    comments=comments,
                    zone=zone,
                    city=city)

                if special_service:
                    l.special_service = special_service

                l.save()

            return super(LineRangeView, self).form_valid(form)
        else:
            return self.form_invalid(form)

line_range = login_required(LineRangeView.as_view())


class LocalCenterListView(ListView):

    document = models.LocalCenter
    paginate_by = 25

localcenter_list = login_required(LocalCenterListView.as_view())


class LocalCenterCreateView(CreateView):

    document = models.LocalCenter
    success_url = reverse_lazy('gesvoip:localcenter_list')

localcenter_create = login_required(LocalCenterCreateView.as_view())


class LocalCenterUpdateView(UpdateView):

    document = models.LocalCenter
    success_url = reverse_lazy('gesvoip:localcenter_list')

localcenter_update = login_required(LocalCenterUpdateView.as_view())


class LocalCenterReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(LocalCenterReportView, self).get_context_data(**kwargs)
        date = dt.date.today().strftime('%Y%m')
        title = 'TL_314_{0}_CL.txt'.format(date)
        items = [
            [i.company.code, date, i.code, i.name]
            for i in models.LocalCenter.objects.all()
        ]
        context.update({'title': title, 'items': items})

        return context

localcenter_report = login_required(LocalCenterReportView.as_view())


class LineServiceReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(LineServiceReportView, self).get_context_data(**kwargs)
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        date = year + month
        title = 'TL_314_{0}_LS.txt'.format(date)
        items = models.Line.get_services(date)
        context.update({'title': title, 'items': items})

        return context

line_service_report = login_required(LineServiceReportView.as_view())


class LineSubscriberReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            LineSubscriberReportView, self).get_context_data(**kwargs)
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        date = year + month
        title = 'VI_314_{0}_SUSCRIPTORES.txt'.format(date)
        items = models.Line.get_subscriptors(date)
        context.update({'title': title, 'items': items})

        return context

line_subscriber_report = login_required(LineSubscriberReportView.as_view())


class CcaaListView(ListView):

    document = models.Ccaa
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(CcaaListView, self).get_context_data(**kwargs)
        context.update({'form_date': forms.ReportForm})

        return context

ccaa_list = login_required(CcaaListView.as_view())


class CcaaCreateView(CreateView):

    document = models.Ccaa
    form_class = forms.CcaaForm
    success_url = reverse_lazy('gesvoip:ccaa_list')

ccaa_create = login_required(CcaaCreateView.as_view())


class CcaaUpdateView(UpdateView):

    document = models.Ccaa
    form_class = forms.CcaaForm
    success_url = reverse_lazy('gesvoip:ccaa_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

ccaa_update = login_required(CcaaUpdateView.as_view())


class CcaaReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(CcaaReportView, self).get_context_data(**kwargs)
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        date = year + month
        title = 'OT_314_{0}_CARGOS_ACC.txt'.format(date)
        items = models.Ccaa.get_report(year, month)
        context.update({'title': title, 'items': items})

        return context

ccaa_report = login_required(CcaaReportView.as_view())


class CdrListView(ListView):

    document = models.Cdr
    paginate_by = 25
    queryset = models.Cdr.objects.all().order_by('-year', '-month')

cdr_list = login_required(CdrListView.as_view())


class LocalTrafficReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            LocalTrafficReportView, self).get_context_data(**kwargs)
        cdr = get_document_or_404(models.Cdr, pk=kwargs.get('pk'))
        title = 'TL_314_%s_TRF_TL.txt' % cdr.get_date()
        items = cdr.get_traffic('local')
        context.update({'title': title, 'items': items})

        return context

local_traffic_report = login_required(LocalTrafficReportView.as_view())


class VoipLocalTrafficReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            VoipLocalTrafficReportView, self).get_context_data(**kwargs)
        cdr = get_document_or_404(models.Cdr, pk=kwargs.get('pk'))
        title = 'VI_314_%s_TRF_TL.txt' % cdr.get_date()
        items = cdr.get_traffic('voip-local')
        context.update({'title': title, 'items': items})

        return context

voip_local_traffic_report = login_required(
    VoipLocalTrafficReportView.as_view())


class MobileTrafficReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            MobileTrafficReportView, self).get_context_data(**kwargs)
        cdr = get_document_or_404(models.Cdr, pk=kwargs.get('pk'))
        title = 'TL_314_%s_TRF_TM.txt' % cdr.get_date()
        items = cdr.get_traffic('movil')
        context.update({'title': title, 'items': items})

        return context

mobile_traffic_report = login_required(MobileTrafficReportView.as_view())


class VoipMobileTrafficReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            VoipMobileTrafficReportView, self).get_context_data(**kwargs)
        cdr = get_document_or_404(models.Cdr, pk=kwargs.get('pk'))
        title = 'VI_314_%s_TRF_TM.txt' % cdr.get_date()
        items = cdr.get_traffic('voip-movil')
        context.update({'title': title, 'items': items})

        return context

voip_mobile_traffic_report = login_required(
    VoipMobileTrafficReportView.as_view())


class NationalTrafficReportView(CSVResponseMixin, generic.TemplateView):

    def get_context_data(self, **kwargs):
        context = super(
            NationalTrafficReportView, self).get_context_data(**kwargs)
        cdr = get_document_or_404(models.Cdr, pk=kwargs.get('pk'))
        title = 'TL_314_%s_TRF_LD.txt' % cdr.get_date()
        items = cdr.get_traffic('internacional')
        context.update({'title': title, 'items': items})

        return context

national_traffic_report = login_required(NationalTrafficReportView.as_view())


class LoadView(generic.TemplateView):

    template_name = 'gesvoip/load.html'

    def get_context_data(self, **kwargs):
        context = super(LoadView, self).get_context_data(**kwargs)
        tasks.load_data.delay()

        return context

load = LoadView.as_view()


class DeleteCdrView(DeleteView):

    document = models.Cdr
    success_url = reverse_lazy('gesvoip:cdr_list')

cdr_delete = login_required(DeleteCdrView.as_view())


class PortabilityUploadView(generic.FormView):

    """ Vista de portability """

    form_class = forms.PortabilityUploadForm
    success_url = reverse_lazy('gesvoip:portability_upload')
    template_name = 'gesvoip/portability_upload.html'

    def form_valid(self, form):
        file_portability = form.cleaned_data.get('file_portability')
        models.Portability.upload(file_portability)

        return super(PortabilityUploadView, self).form_valid(form)

portability_upload = login_required(PortabilityUploadView.as_view())


class NumerationUploadView(generic.FormView):

    """ Vista de carga de numeracion """

    form_class = forms.NumerationUploadForm
    success_url = reverse_lazy('gesvoip:numeration_upload')
    template_name = 'gesvoip/numeration_upload.html'

    def form_valid(self, form):
        file_numeration = form.cleaned_data.get('file_numeration')
        models.Numeration.upload(file_numeration)

        return super(NumerationUploadView, self).form_valid(form)

numeration_upload = login_required(NumerationUploadView.as_view())
