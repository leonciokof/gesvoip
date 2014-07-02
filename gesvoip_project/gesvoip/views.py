import csv
import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic

from mongogeneric import CreateView, DetailView, ListView, UpdateView
import django_rq

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

new_rate = login_required(NewRateView.as_view())


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
        # tasks.insert_incoming.delay(cdr)
        django_rq.enqueue(tasks.insert_incoming, cdr, timeout=60 * 60 * 60)

        return super(NewCdrView, self).form_valid(form)

new_cdr = login_required(NewCdrView.as_view())


class IncomingListView(ListView):

    document = models.Incoming
    paginate_by = 10

incoming_list = login_required(IncomingListView.as_view())


class InvoiceListView(ListView):

    document = models.Invoice
    paginate_by = 10

invoice_list = login_required(InvoiceListView.as_view())


class CompanyListView(ListView):

    document = models.Company
    paginate_by = 10

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
        initial.update({
            'bussines_normal_start': self.object.schedules[
                'bussines']['normal']['start'],
            'bussines_normal_end': self.object.schedules[
                'bussines']['normal']['end'],
            'bussines_reduced_start': self.object.schedules[
                'bussines']['reduced']['start'],
            'bussines_reduced_end': self.object.schedules[
                'bussines']['reduced']['end'],
            'bussines_nightly_start': self.object.schedules[
                'bussines']['nightly']['start'],
            'bussines_nightly_end': self.object.schedules[
                'bussines']['nightly']['end'],
            'saturday_normal_start': self.object.schedules[
                'saturday']['normal']['start'],
            'saturday_normal_end': self.object.schedules[
                'saturday']['normal']['end'],
            'saturday_reduced_start': self.object.schedules[
                'saturday']['reduced']['start'],
            'saturday_reduced_end': self.object.schedules[
                'saturday']['reduced']['end'],
            'saturday_nightly_start': self.object.schedules[
                'saturday']['nightly']['start'],
            'saturday_nightly_end': self.object.schedules[
                'saturday']['nightly']['end'],
            'festive_normal_start': self.object.schedules[
                'festive']['normal']['start'],
            'festive_normal_end': self.object.schedules[
                'festive']['normal']['end'],
            'festive_reduced_start': self.object.schedules[
                'festive']['reduced']['start'],
            'festive_reduced_end': self.object.schedules[
                'festive']['reduced']['end'],
            'festive_nightly_start': self.object.schedules[
                'festive']['nightly']['start'],
            'festive_nightly_end': self.object.schedules[
                'festive']['nightly']['end'],
        })
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
    paginate_by = 10

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
    paginate_by = 10

    def get_queryset(self):
        queryset = super(NumerationListView, self).get_queryset()
        company = models.Company.objects.get(pk=self.kwargs.get('pk'))
        return queryset.filter(company=company)

numeration_list = login_required(NumerationListView.as_view())


class IncomingValidListView(ListView):

    document = models.Incoming
    paginate_by = 10

    def get_queryset(self):
        queryset = super(IncomingValidListView, self).get_queryset()
        invoice = models.Invoice.objects.get(pk=self.kwargs.get('pk'))
        cdr = models.Cdr.objects.get(year=invoice.year, month=invoice.month)
        return queryset.filter(cdr=cdr, company=invoice.company, invoiced=True)

incoming_valid_list = login_required(IncomingValidListView.as_view())


class LineListView(ListView):

    document = models.Line
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(LineListView, self).get_context_data(**kwargs)
        context.update({'form_date': forms.ReportForm})

        return context

line_list = login_required(LineListView.as_view())


class LineCreateView(CreateView):

    document = models.Line
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
    paginate_by = 10

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
        date = dt.date.today().strftime('%Y-%m')
        title = 'TL_314_{0}_CL.txt'.format(date)
        items = [
            [i.company, date, i.code, i.name]
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
    paginate_by = 10

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
