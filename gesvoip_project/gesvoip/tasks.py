from __future__ import absolute_import

from celery import task

import csv
import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage

from raven import Client
import pysftp
import queries

from . import choices, models

dsn = settings.RAVEN_CONFIG['dsn'] if not settings.DEBUG else ''
client = Client(dsn)


def load_portability():
    with pysftp.Connection(
            settings.TEP_HOST, username=settings.TEP_USERNAME,
            password=settings.TEP_PASSWORD) as sftp:
        today = dt.date.today().strftime('%Y%m%d')
        tep_file = 'Dailyfiles/TEP_%s.txt' % today
        destination = '/tmp/TEP_%s.txt' % today
        sftp.get(tep_file, destination)

        with open(destination, 'rb') as f:
            f.next()
            reader = csv.DictReader(f, delimiter=';')
            reader.fieldnames = 'date', 'number', 'type', 'company'
            models.Portability.create(reader)


def insert_cdr(cdr):
    # Carga previa de portados
    load_portability()

    for c in choices.COMPANIAS:
        cdr.insert_incoming(c[0])

    for c in models.Company.objects(invoicing='monthly'):
        i = models.Invoice.objects.get(
            company=c, month=cdr.month, year=cdr.year)

        for p in models.Period.objects(invoice=i):
            for r in models.Rate.objects(period=p):
                r.call_number = models.Incoming.objects(
                    company=c,
                    connect_time__gte=p.start.date(),
                    connect_time__lte=p.end.date(),
                    schedule=r._type).count()
                r.call_duration = models.Incoming.objects(
                    company=c,
                    connect_time__gte=p.start.date(),
                    connect_time__lte=p.end.date(),
                    schedule=r._type).sum('ingress_duration')
                r.total = r.call_duration * r.price
                r.save()

            p.call_number = models.Rate.objects(
                period=p).sum('call_number')
            p.call_duration = models.Rate.objects(
                period=p).sum('call_duration')
            p.total = models.Rate.objects(period=p).sum('total')
            p.save()

        i.call_number = models.Period.objects(
            invoice=i).sum('call_number')
        i.call_duration = models.Period.objects(
            invoice=i).sum('call_duration')
        i.total = models.Period.objects(invoice=i).sum('total')
        i.invoiced = True
        i.save()

    cdr.insert_outgoing()
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


@task()
def load_data():
    try:
        session_sti = queries.Session(settings.STI_URL)

        with queries.Session(settings.GESVOIP_URL) as session:
            models.Cdr.objects.delete()
            models.Company.objects.delete()
            models.Incoming.objects.delete()
            models.Outgoing.objects.delete()
            models.Invoice.objects.delete()
            models.Period.objects.delete()
            models.Rate.objects.delete()
            models.Holiday.objects.delete()
            models.Line.objects.delete()
            models.Ccaa.objects.delete()

            for h in session.query('SELECT fecha FROM feriado'):
                date = h.get('fecha')
                holiday = models.Holiday(date=date)
                holiday.save()

            for c in session.query(
                    'SELECT DISTINCT(fecha) FROM log_llamadas ORDER BY fecha'):
                date = c.get('fecha')
                year = date[:4]
                month = date[5:]
                cdr = models.Cdr(year=year, month=month, processed=True)
                cdr.save()

            for c in session.query(
                    'SELECT id_compania, nombre, id, codigo '
                    'FROM compania WHERE id IS NOT NULL'):
                id_compania = c.get('id_compania')
                name = c.get('nombre')
                idoidd = c.get('id')
                code = c.get('codigo')
                company = models.Company(name=name, idoidd=idoidd, code=code)
                company.save()

                q = 'SELECT zona, rango FROM numeracion WHERE compania=%s' % (
                    id_compania,)

                for n in session.query(q):
                    zone = n.get('zona')
                    _range = n.get('rango')
                    numeration = models.Numeration(
                        zone=zone, _range=_range, company=company)
                    numeration.save()

                q = (
                    'SELECT connect_time, ani_number, ingress_duration, '
                    'dialed_number, estado, motivo, tipo, fecha '
                    'FROM log_llamadas WHERE estado != \'facturado\' '
                    'and compania_ani = \'%s\'' % id_compania)

                for l in session.query(q):
                    connect_time = l.get('connect_time')
                    ani_number = l.get('ani_number')
                    ingress_duration = l.get('ingress_duration')
                    dialed_number = l.get('dialed_number')
                    estado = l.get('estado')
                    valid = True if estado == 'activado' else False
                    motivo = l.get('motivo')
                    observation = None if motivo == '' else motivo
                    tipo = l.get('tipo')
                    date = l.get('fecha')
                    year = date[:4]
                    month = date[5:]
                    cdr = models.Cdr.objects.get(year=year, month=month)
                    numeration = models.Incoming(
                        connect_time=connect_time, ani_number=ani_number,
                        ingress_duration=ingress_duration,
                        dialed_number=dialed_number, valid=valid,
                        observation=observation, company=company, _type=tipo,
                        cdr=cdr, schedule=None)
                    numeration.save()

                q = (
                    'SELECT origen, destino, fecha, hora, duracion, horario '
                    'FROM det_factura WHERE compania = \'%s\'' % id_compania)

                for l in session.query(q):
                    fecha = l.get('fecha')
                    hora = l.get('hora')
                    connect_time = dt.datetime.strptime(
                        fecha + hora, '%Y-%m-%d%H:%M:%S')
                    ani_number = l.get('origen')
                    ingress_duration = l.get('duracion')
                    dialed_number = l.get('destino')
                    year = fecha[:4]
                    month = fecha[5:][:2]
                    schedule = l.get('horario')
                    cdr = models.Cdr.objects.get(year=year, month=month)
                    numeration = models.Incoming(
                        connect_time=connect_time, ani_number=ani_number,
                        ingress_duration=ingress_duration,
                        dialed_number=dialed_number, valid=True,
                        company=company,
                        cdr=cdr, schedule=schedule, invoiced=True)
                    numeration.save()

                q = (
                    'SELECT id_factura, fecha_inicio, fecha_fin, tarifa, '
                    'valor_normal, valor_reducido, valor_nocturno '
                    'FROM factura WHERE compania = %s' % id_compania)

                for f in session.query(q):
                    id_factura = f.get('id_factura')
                    fecha_inicio = f.get('fecha_inicio')
                    fecha_fin = f.get('fecha_fin')
                    tarifa = f.get('tarifa')
                    valor_normal = f.get('valor_normal')
                    valor_reducido = f.get('valor_reducido')
                    valor_nocturno = f.get('valor_nocturno')
                    date = fecha_inicio[0]
                    year = date.strftime('%Y')
                    month = date.strftime('%m')

                    i = models.Invoice(
                        year=year, month=motivo, code=id_factura,
                        company=company, invoiced=True)
                    i.save()

                    i_call_number = 0
                    i_call_duration = 0
                    i_total = 0

                    for i, fi in enumerate(fecha_inicio):
                        call_number = 0
                        call_duration = 0
                        total = valor_normal[i] + valor_reducido[
                            i] + valor_nocturno[i]
                        qq = (
                            'SELECT valor_normal, valor_reducido, '
                            'valor_nocturno FROM tarifa WHERE id_ingreso = %s '
                            'and fecha = %s' % (tarifa[i], fi))
                        t = session.query(qq).as_dict()
                        qq = (
                            'SELECT COUNT(*) FROM det_factura '
                            'WHERE factura=%s and horario=\'normal\' '
                            'and fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        count = session.query(qq).as_dict().get('count')
                        call_number += count
                        qq = (
                            'SELECT SUM(duracion) FROM det_factura '
                            'WHERE factura=%s and horario = \'normal\' and '
                            'fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        suma = session.query(qq).as_dict().get('sum')
                        call_duration += suma
                        r1 = models.Rate(
                            price=t.get('valor_normal'), _type='normal',
                            call_number=count, call_duration=suma,
                            total=valor_normal[i])
                        qq = (
                            'SELECT COUNT(*) FROM det_factura '
                            'WHERE factura = %s and horario = \'reducido\' '
                            'and fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        count = session.query(qq).as_dict().get('count')
                        call_number += count
                        qq = (
                            'SELECT SUM(duracion) FROM det_factura '
                            'WHERE factura= %s and horario = \'reducido\' '
                            'and fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        suma = session.query(qq).as_dict().get('sum')
                        call_duration += suma
                        r2 = models.Rate(
                            price=t.get('valor_reducido'), _type='reducido',
                            call_number=count, call_duration=suma,
                            total=valor_reducido[i])
                        qq = (
                            'SELECT COUNT(*) FROM det_factura '
                            'WHERE factura = %s and horario = \'nocturno\' '
                            'and fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        count = session.query(qq).as_dict().get('count')
                        call_number += count
                        qq = (
                            'SELECT SUM(duracion) FROM det_factura '
                            'WHERE factura = %s and horario = \'nocturno\' '
                            'and fecha between %s and '
                            '%s' % (id_factura, fi, fecha_fin[i]))
                        suma = session.query(qq).as_dict().get('sum')
                        call_duration += suma
                        r3 = models.Rate(
                            price=t.get('valor_nocturno'), _type='nocturno',
                            call_number=count, call_duration=suma,
                            total=valor_nocturno[i])
                        p = models.Period(
                            invoice=i, start=fi, end=fecha_fin[i],
                            call_number=call_number,
                            call_duration=call_duration,
                            total=total)
                        i_total += total
                        i_call_duration += call_duration
                        i_call_number += call_number
                        p.save()
                        r1.period = p
                        r2.period = p
                        r3.period = p
                        r1.save()
                        r2.save()
                        r3.save()

                    i.call_duration = i_call_duration
                    i.call_number = i_call_number
                    i.total = i_total
                    i.save()

                q = (
                    'SELECT fecha, hora, ani_number, ingress_duration, '
                    'final_number, estado, descripcion, fecha_cdr '
                    'FROM log_llamadas WHERE idd = \'%s\'' % id_compania)

                for l in session_sti.query(q):
                    fecha = l.get('fecha')
                    hora = l.get('hora')
                    connect_time = dt.datetime.strptime(
                        fecha + hora, '%Y-%m-%d%H:%M:%S')
                    ani_number = l.get('ani_number')
                    ingress_duration = l.get('ingress_duration')
                    final_number = l.get('final_number')
                    estado = l.get('estado')
                    valid = True if estado == 'activado' else False
                    observation = None if motivo == '' else motivo
                    tipo = l.get('descripcion')
                    date = l.get('fecha_cdr')
                    year = date[:4]
                    month = date[5:]
                    cdr = models.Cdr.objects.get(year=year, month=month)
                    numeration = models.Outgoing(
                        connect_time=connect_time, ani_number=ani_number,
                        ingress_duration=ingress_duration,
                        final_number=final_number, valid=valid,
                        company=company, _type=tipo,
                        cdr=cdr, schedule=None)
                    numeration.save()

                q = 'SELECT * FROM ccaa WHERE concecionaria = \'%s\'' % (
                    company.code)

                for l in session_sti.query(q):
                    periodo = l.get('periodo')
                    invoice = l.get('n_factura')
                    fecha_inicio = l.get('fecha_inicio')
                    fecha_fin = l.get('fecha_fin')
                    fecha_fact = l.get('fecha_fact')
                    start = dt.datetime.strptime(fecha_inicio, '%Y%m%d')
                    end = dt.datetime.strptime(fecha_fin, '%Y%m%d')
                    invoice_date = dt.datetime.strptime(fecha_fact, '%Y%m%d')
                    horario = l.get('horario')

                    if horario == 'N':
                        schedule = 'normal'

                    elif horario == 'O':
                        schedule = 'nocturno'

                    else:
                        schedule = 'reducido'

                    call_duration = l.get('trafico')
                    total = l.get('monto')

                    year = periodo[:4]
                    month = periodo[5:]
                    ccaa = models.Ccaa(
                        year=year, month=month,
                        invoice=invoice,
                        start=start, end=end,
                        company=company, invoice_date=invoice_date,
                        schedule=schedule, call_duration=call_duration,
                        total=total)
                    ccaa.save()

            for l in session_sti.query('SELECT * FROM lineas'):
                number = l.get('numero')
                name = l.get('nombre')
                entity = l.get('tipo_persona')
                entity = entity.lower() if entity else None
                comments = l.get('comentarios')
                zone = l.get('area')
                city = l.get('comuna')
                line = models.Line(
                    number=number, name=name, entity=entity, comments=comments,
                    zone=zone, city=city)
                line.save()

        send_email(
            [{'name': 'Leonardo', 'email': 'lgaticastyle@gmail.com'}],
            'Proceso finalizado',
            'gesvoip_success',
            {})

    except Exception:
        client.captureException()
