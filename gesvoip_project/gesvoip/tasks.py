import csv
import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage

import pysftp
import queries

from . import choices, models


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


def load_data():
    with queries.Session(settings.GESVOIP_URL) as session:
        for c in session.query(
                'SELECT DISTINCT(fecha) FROM log_llamadas ORDER BY fecha'):
            date = c.get('fecha')
            year = date[:4]
            month = date[5:]
            cdr = models.Cdr(year=year, month=month, processed=True)
            cdr.save()

        models.Company.objects.delete()

        for c in session.query(
                'SELECT id_compania, nombre, id FROM compania IS NOT NULL'):
            id_compania = c.get('id_compania')
            name = c.get('nombre')
            code = c.get('id')

            if name and code:
                company = models.Company(name=name, code=int(code))
                company.save()

            q = 'SELECT zona, rango FROM numeracion WHERE compania = %s' % (
                id_compania,)

            for n in session.query(q):
                zone = n.get('zona')
                _range = n.get('rango')

                if zone and _range:
                    numeration = models.Numeration(
                        zone=int(zone), _range=int(_range), company=company)
                    numeration.save()

            q = (
                'SELECT id_log, connect_time, ani_number, ingress_duration, '
                'dialed_number, estado, motivo, tipo, fecha FROM log_llamadas '
                'WHERE compania_ani = \'%s\'' % id_compania)

            for l in session.query(q):
                id_log = l.get('id_log')
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

                qq = (
                    'SELECT horario FROM det_factura WHERE id_detalle = '
                    '%s' % id_log)

                df = session.query(qq).as_dict()

                numeration = models.Incoming(
                    connect_time=connect_time, ani_number=ani_number,
                    ingress_duration=ingress_duration,
                    dialed_number=dialed_number, valid=valid,
                    observation=observation, company=company, _type=tipo,
                    cdr=cdr, schedule=df.get('horario'))
                numeration.save()

            q = (
                'SELECT id_factura, fecha_inicio, fecha_fin, tarifa, '
                'valor_normal, valor_reducido, valor_nocturno FROM factura '
                'WHERE compania = %s' % id_compania)

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
                    year=year, month=motivo, code=id_factura, company=company,
                    invoiced=True)
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
                        'SELECT valor_normal, valor_reducido, valor_nocturno '
                        'FROM tarifa WHERE id_ingreso = %s and fecha = '
                        '%s' % (tarifa[i], fi))
                    t = session.query(qq).as_dict()
                    qq = (
                        'SELECT COUNT(*) FROM det_factura WHERE factura = %s '
                        'and horario = \'normal\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    count = session.query(qq).as_dict().get('count')
                    call_number += count
                    qq = (
                        'SELECT SUM(duracion) FROM det_factura WHERE factura= '
                        '%s and horario = \'normal\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    suma = session.query(qq).as_dict().get('sum')
                    call_duration += suma
                    r1 = models.Rate(
                        price=t.get('valor_normal'), _type='normal',
                        call_number=count, call_duration=suma,
                        total=valor_normal[i])
                    qq = (
                        'SELECT COUNT(*) FROM det_factura WHERE factura = %s '
                        'and horario = \'reducido\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    count = session.query(qq).as_dict().get('count')
                    call_number += count
                    qq = (
                        'SELECT SUM(duracion) FROM det_factura WHERE factura= '
                        '%s and horario = \'reducido\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    suma = session.query(qq).as_dict().get('sum')
                    call_duration += suma
                    r2 = models.Rate(
                        price=t.get('valor_reducido'), _type='reducido',
                        call_number=count, call_duration=suma,
                        total=valor_reducido[i])
                    qq = (
                        'SELECT COUNT(*) FROM det_factura WHERE factura = %s '
                        'and horario = \'nocturno\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    count = session.query(qq).as_dict().get('count')
                    call_number += count
                    qq = (
                        'SELECT SUM(duracion) FROM det_factura WHERE factura= '
                        '%s and horario = \'nocturno\' fecha between %s and '
                        '%s' % (id_factura, fi, fecha_fin[i]))
                    suma = session.query(qq).as_dict().get('sum')
                    call_duration += suma
                    r3 = models.Rate(
                        price=t.get('valor_nocturno'), _type='nocturno',
                        call_number=count, call_duration=suma,
                        total=valor_nocturno[i])
                    p = models.Period(
                        invoice=i, start=fi, end=fecha_fin[i],
                        call_number=call_number, call_duration=call_duration,
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
