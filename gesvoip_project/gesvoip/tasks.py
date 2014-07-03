from django.conf import settings
from django.core.mail import EmailMessage

from . import models


def insert_incoming(cdr):
    for name in ['ENTEL']:
        cdr.insert_incoming(name)

    for c in models.Company.objects.filter(invoicing='monthly'):
        i = models.Invoice.objects.get(
            company=c, month=cdr.month, year=cdr.year)

        for p in models.Period.objects.filter(invoice=i):
            for r in models.Rate.objects.filter(period=p):
                r.call_number = models.Incoming.objects.filter(
                    company=c,
                    connect_time__gte=p.start.date(),
                    connect_time__lte=p.end.date(),
                    schedule=r._type).count()
                r.call_duration = models.Incoming.objects.filter(
                    company=c,
                    connect_time__gte=p.start.date(),
                    connect_time__lte=p.end.date(),
                    schedule=r._type).sum('ingress_duration')
                r.total = r.call_duration * r.price
                r.save()

            p.call_number = models.Rate.objects.filter(
                period=p).sum('call_number')
            p.call_duration = models.Rate.objects.filter(
                period=p).sum('call_duration')
            p.total = models.Rate.objects.filter(period=p).sum('total')
            p.save()

        i.call_number = models.Period.objects.filter(
            invoice=i).sum('call_number')
        i.call_duration = models.Period.objects.filter(
            invoice=i).sum('call_duration')
        i.total = models.Period.objects.filter(invoice=i).sum('total')
        i.invoiced = True
        i.save()

    send_email(
        [{'name': 'Leonardo Gatica', 'email': 'lgaticastyle@gmail.com'}],
        'Proceso finalizado',
        'gesvoip_success',
        {})


def send_email(to, subject, template_name, global_merge_vars):
    """Envia emails."""
    msg = EmailMessage(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to)
    msg.template_name = template_name
    msg.global_merge_vars = global_merge_vars
    msg.send()
