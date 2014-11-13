from __future__ import absolute_import
import os

from celery import task

import csv
import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage

from raven import Client
import pysftp
import psycopg2

from . import choices, models

dsn = settings.RAVEN_CONFIG['dsn'] if not settings.DEBUG else ''
client = Client(dsn)
conn = psycopg2.connect("dbname=gesvoip user=postgres password=serveradmin")
conn_sti = psycopg2.connect("dbname=sti user=postgres password=serveradmin")


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
        ['Leonardo Gatica <lgaticastyle@gmail.com>'],
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
        # models.Cdr.objects.delete()
        # models.Company.objects.delete()
        # models.Incoming.objects.delete()
        # models.Outgoing.objects.delete()
        # models.Invoice.objects.delete()
        # models.Period.objects.delete()
        # models.Rate.objects.delete()
        # models.Holiday.objects.delete()
        # models.Line.objects.delete()
        # models.Ccaa.objects.delete()

        # cur_holiday = conn.cursor()
        # cur_holiday.execute('SELECT fecha FROM feriado')
        # for h in cur_holiday.fetchall():
        #     date = h[0]
        #     holiday = models.Holiday(date=date)
        #     holiday.save()
        # cur_holiday.close()
        # cur_log_llamadas = conn.cursor()
        # cur_log_llamadas.execute(
        #     'SELECT DISTINCT(fecha) FROM log_llamadas ORDER BY fecha')
        # for c in cur_log_llamadas.fetchall():
        #     date = c[0]
        #     year = date[:4]
        #     month = date[5:]
        #     cdr = models.Cdr(year=year, month=month, processed=True)
        #     cdr.save()
        # cur_log_llamadas.close()
        # cur_compania = conn.cursor()
        # cur_compania.execute(
        #     'SELECT id_compania, nombre, id, codigo '
        #     'FROM compania')
        # for c in cur_compania.fetchall():
        #     id_compania = c[0]
        #     name = c[1]
        #     idoidd = c[2]
        #     code = c[3]
        #     company = models.Company(
        #         name=name, idoidd=idoidd, code=code, id_compania=id_compania)
        #     company.save()
        # cur_compania.close()
        # cur_numeracion = conn.cursor()
        # cur_numeracion.execute('SELECT zona, rango, compania FROM
        # numeracion')

        # for n in cur_numeracion.fetchall():
        #     zone = n[0]
        #     _range = n[1]
        #     id_compania = n[2]
        #     company = models.Company.objects.filter(
        #         id_compania=id_compania).first()
        #     numeration = models.Numeration(
        #         zone=zone, _range=_range, company=company)
        #     numeration.save()
        # cur_numeracion.close()
        # cur_log_llamadas2 = conn.cursor()
        # cur_log_llamadas2.execute(
        #     'SELECT connect_time, ani_number, ingress_duration, '
        #     'dialed_number, estado, motivo, tipo, fecha, compania_ani '
        #     'FROM log_llamadas WHERE estado != \'facturado\'')

        # for l in cur_log_llamadas2.fetchall():
        #     connect_time = l[0]
        #     ani_number = l[1]
        #     ingress_duration = l[2]
        #     dialed_number = l[3]
        #     estado = l[4]
        #     valid = True if estado == 'activado' else False
        #     motivo = l[5]
        #     observation = None if motivo == '' else motivo
        #     tipo = l[6]
        #     date = l[7]
        #     id_compania = l[8]
        #     id_compania = None if id_compania == '' else id_compania
        #     year = date[:4]
        #     month = date[5:]
        #     company = models.Company.objects.filter(
        #         id_compania=id_compania).first()
        #     cdr = models.Cdr.objects.get(year=year, month=month)
        #     numeration = models.Incoming(
        #         connect_time=connect_time, ani_number=ani_number,
        #         ingress_duration=ingress_duration,
        #         dialed_number=dialed_number, valid=valid,
        #         observation=observation, company=company, _type=tipo,
        #         cdr=cdr, schedule=None)
        #     numeration.save()
        # cur_log_llamadas2.close()
        for invoice in models.Invoice.objects(
                year='2013', month__in=['11', '12']):
            cur_det_factura = conn.cursor()
            cur_det_factura.execute(
                'SELECT origen, destino, fecha, hora, duracion, horario, '
                'compania FROM det_factura WHERE factura=%s', (invoice.code,))

            for l in cur_det_factura.fetchall():
                ani_number = str(l[0])
                dialed_number = str(l[1])
                fecha = l[2]
                hora = l[3]
                connect_time = dt.datetime.strptime(
                    '%s %s' % (fecha.strftime('%Y-%m-%d'), hora),
                    '%Y-%m-%d %H:%M:%S')
                ingress_duration = l[4]
                year = fecha.strftime('%Y')
                month = fecha.strftime('%m')
                schedule = l[5]
                id_compania = l[6]
                company = models.Company.objects.filter(
                    id_compania=id_compania).first()
                cdr = models.Cdr.objects.get(year=year, month=month)
                numeration = models.Incoming(
                    connect_time=connect_time, ani_number=ani_number,
                    ingress_duration=ingress_duration,
                    dialed_number=dialed_number, valid=True,
                    company=company,
                    cdr=cdr, schedule=schedule, invoiced=True)
                numeration.save()
            cur_det_factura.close()
        # cur_factura = conn.cursor()
        # cur_factura.execute(
        #     'SELECT id_factura, fecha_inicio, fecha_fin, tarifa, '
        #     'valor_normal, valor_reducido, valor_nocturno, compania '
        #     'FROM factura')

        # for f in cur_factura.fetchall():
        #     id_factura = f[0]
        #     fecha_inicio = f[1]
        #     fecha_fin = f[2]
        #     tarifa = f[3]
        #     valor_normal = f[4]
        #     valor_reducido = f[5]
        #     valor_nocturno = f[6]
        #     id_compania = f[7]
        #     date = fecha_inicio[0]
        #     year = date.strftime('%Y')
        #     month = date.strftime('%m')
        #     company = models.Company.objects.filter(
        #         id_compania=id_compania).first()
        #     invoice = models.Invoice(
        #         year=year, month=month, code=id_factura,
        #         company=company, invoiced=True)
        #     invoice.save()

        #     i_call_number = 0
        #     i_call_duration = 0
        #     i_total = 0.0

        #     for i, fi in enumerate(fecha_inicio):
        #         call_number = 0
        #         call_duration = 0
        #         total = valor_normal[i] + valor_reducido[
        #             i] + valor_nocturno[i]
        #         cur_tarifa = conn.cursor()
        #         cur_tarifa.execute(
        #             'SELECT valor_normal, valor_reducido, '
        #             'valor_nocturno FROM tarifa WHERE id_tarifa = %s '
        #             'and fecha = %s', (tarifa[i], fi))
        #         t = cur_tarifa.fetchone()
        #         tarifa_valor_normal = t[0]
        #         tarifa_valor_reducido = t[1]
        #         tarifa_valor_nocturno = t[2]
        #         cur_tarifa.close()
        #         cur_set_factura_count_normal = conn.cursor()
        #         cur_set_factura_count_normal.execute(
        #             'SELECT COUNT(*) FROM det_factura '
        #             'WHERE factura=%s and horario=\'normal\' '
        #             'and fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         count = cur_set_factura_count_normal.fetchone()[0]
        #         cur_set_factura_count_normal.close()
        #         call_number += count
        #         cur_set_factura_sum_normal = conn.cursor()
        #         cur_set_factura_sum_normal.execute(
        #             'SELECT SUM(duracion) FROM det_factura '
        #             'WHERE factura=%s and horario = \'normal\' and '
        #             'fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         suma = cur_set_factura_sum_normal.fetchone()[0]
        #         suma = 0 if suma is None else suma
        #         cur_set_factura_sum_normal.close()
        #         call_duration += suma
        #         r1 = models.Rate(
        #             price=tarifa_valor_normal, _type='normal',
        #             call_number=count, call_duration=suma,
        #             total=valor_normal[i])
        #         cur_set_factura_count_reducido = conn.cursor()
        #         cur_set_factura_count_reducido.execute(
        #             'SELECT COUNT(*) FROM det_factura '
        #             'WHERE factura = %s and horario = \'reducido\' '
        #             'and fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         count = cur_set_factura_count_reducido.fetchone()[0]
        #         cur_set_factura_count_reducido.close()
        #         call_number += count
        #         cur_set_factura_sum_reducido = conn.cursor()
        #         cur_set_factura_sum_reducido.execute(
        #             'SELECT SUM(duracion) FROM det_factura '
        #             'WHERE factura= %s and horario = \'reducido\' '
        #             'and fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         suma = cur_set_factura_sum_reducido.fetchone()[0]
        #         suma = 0 if suma is None else suma
        #         cur_set_factura_sum_reducido.close()
        #         call_duration += suma
        #         r2 = models.Rate(
        #             price=tarifa_valor_reducido, _type='reducido',
        #             call_number=count, call_duration=suma,
        #             total=valor_reducido[i])
        #         cur_set_factura_count_nocturno = conn.cursor()
        #         cur_set_factura_count_nocturno.execute(
        #             'SELECT COUNT(*) FROM det_factura '
        #             'WHERE factura = %s and horario = \'nocturno\' '
        #             'and fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         count = cur_set_factura_count_nocturno.fetchone()[0]
        #         cur_set_factura_count_nocturno.close()
        #         call_number += count
        #         cur_set_factura_sum_nocturno = conn.cursor()
        #         cur_set_factura_sum_nocturno.execute(
        #             'SELECT SUM(duracion) FROM det_factura '
        #             'WHERE factura = %s and horario = \'nocturno\' '
        #             'and fecha between %s and '
        #             '%s', (id_factura, fi, fecha_fin[i]))
        #         suma = cur_set_factura_sum_nocturno.fetchone()[0]
        #         suma = 0 if suma is None else suma
        #         cur_set_factura_sum_nocturno.close()
        #         call_duration += suma
        #         r3 = models.Rate(
        #             price=tarifa_valor_nocturno, _type='nocturno',
        #             call_number=count, call_duration=suma,
        #             total=valor_nocturno[i])
        #         p = models.Period(
        #             invoice=invoice, start=fi, end=fecha_fin[i],
        #             call_number=call_number,
        #             call_duration=call_duration,
        #             total=total)
        #         i_total += float(total)
        #         i_call_duration += call_duration
        #         i_call_number += call_number
        #         p.save()
        #         r1.period = p
        #         r2.period = p
        #         r3.period = p
        #         r1.save()
        #         r2.save()
        #         r3.save()

        #     invoice.call_duration = i_call_duration
        #     invoice.call_number = i_call_number
        #     invoice.total = i_total
        #     invoice.save()

        # cur_factura.close()
        # cur_cdr = conn_sti.cursor()
        # cur_cdr.execute(
        #     'SELECT fecha, hora, ani_number, ingress_duration, '
        #     'final_number, estado, descripcion, fecha_cdr, idd '
        #     'FROM cdr')

        # for l in cur_cdr.fetchall():
        #     fecha = l[0]
        #     hora = l[1]
        #     connect_time = dt.datetime.combine(fecha, hora)
        #     ani_number = l[2]
        #     if ani_number is not None:
        #         ani_number = str(ani_number)
        #     ingress_duration = l[3]
        #     final_number = l[4]
        #     estado = l[5]
        #     valid = True if estado == 'activado' else False
        #     tipo = l[6]
        #     date = l[7]
        #     id_compania = l[8]
        #     year = date[:4]
        #     month = date[5:]
        #     company = models.Company.objects.filter(
        #         id_compania=id_compania).first()
        #     cdr = models.Cdr.objects.get(year=year, month=month)
        #     outgoing = models.Outgoing(
        #         connect_time=connect_time, ani_number=ani_number,
        #         ingress_duration=ingress_duration,
        #         final_number=final_number, valid=valid,
        #         company=company, _type=tipo,
        #         cdr=cdr, schedule=None)
        #     outgoing.save()

        # cur_cdr.close()
        # cur_ccaa = conn_sti.cursor()
        # cur_ccaa.execute(
        #     'SELECT periodo, n_factura, fecha_inicio, fecha_fin, '
        #     'fecha_fact, horario, trafico, monto, concecionaria FROM ccaa')

        # for l in cur_ccaa.fetchall():
        #     periodo = l[0]
        #     invoice = l[1]
        #     fecha_inicio = l[2]
        #     fecha_fin = l[3]
        #     fecha_fact = l[4]
        #     start = dt.datetime.strptime(fecha_inicio, '%Y%m%d')
        #     end = dt.datetime.strptime(fecha_fin, '%Y%m%d')
        #     invoice_date = dt.datetime.strptime(fecha_fact, '%Y%m%d')
        #     horario = l[5]

        #     if horario == 'N':
        #         schedule = 'normal'

        #     elif horario == 'O':
        #         schedule = 'nocturno'

        #     else:
        #         schedule = 'reducido'

        #     call_duration = l[6]
        #     total = l[7]
        #     code = l[8]
        #     year = periodo[:4]
        #     month = periodo[4:]
        #     company = models.Company.objects.filter(code=code).first()
        #     ccaa = models.Ccaa(
        #         year=year, month=month,
        #         invoice=invoice,
        #         start=start, end=end,
        #         company=company, invoice_date=invoice_date,
        #         schedule=schedule, call_duration=call_duration,
        #         total=total)
        #     ccaa.save()

        # cur_ccaa.close()
        # cur_lineas = conn_sti.cursor()
        # cur_lineas.execute(
        #     'SELECT numero, nombre, tipo_persona, comentarios, area, comuna '
        #     'FROM lineas')

        # for l in cur_lineas.fetchall():
        #     number = l[0]
        #     if number is not None:
        #         number = str(number)
        #     name = l[1]
        #     entity = l[2]
        #     entity = entity.lower() if entity else None
        #     comments = l[3]
        #     zone = l[4]
        #     city = l[5]
        #     if zone == '':
        #         zone = None
        #     if city == '':
        #         city = None
        #     line = models.Line(
        #         number=number, name=name, entity=entity, comments=comments,
        #         zone=zone, city=city)
        #     line.save()

        # cur_lineas.close()
        conn.close()
        conn_sti.close()

        send_email(
            ['Leonardo Gatica <lgaticastyle@gmail.com>'],
            'Proceso finalizado',
            'gesvoip_success',
            {})

    except Exception:
        client.captureException()


def load_communes():
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'comunas.csv')
    with open(filename, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        communes = map(lambda x: models.Commune(**x), reader)
        models.Commune.objects.insert(communes)
