# -*- coding: utf-8 -*-

from calendar import monthrange
from dateutil.rrule import rrule, DAILY
from re import search
import datetime as dt

from django.db import connection, models
from django.db.models import Max, Min, Sum

from djorm_pgarray.fields import ArrayField
from nptime import nptime
import mongoengine

from . import choices, patterns
from sti.models import Lineas

mongoengine.connect('gesvoip')


class Cdr(models.Model):

    def update_filename(instance, filename):
        return 'logs/{0}-{1}-{2}.log'.format(
            instance.year, instance.month, instance.compania)

    id = models.AutoField(primary_key=True)
    fecha = models.CharField(max_length=255, blank=True)
    compania = models.CharField(max_length=255, choices=choices.COMPANIAS)
    month = models.CharField(
        max_length=2, choices=choices.MONTHS, default='', blank=True)
    year = models.CharField(
        max_length=4, choices=choices.YEARS, default='', blank=True)
    source = models.FileField(
        upload_to=update_filename, blank=True, null=True)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'cdr'
        verbose_name = 'cdr'
        verbose_name_plural = 'cdrs'

    def __unicode__(self):
        return u'{0} {1}'.format(self.fecha, self.compania)

    def valida_ani(self, ani):
        if len(ani) == 11:
            return True

        else:
            return False

    def get_activado_ctc(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if search(patterns.pattern_569, ani):
            return 'activado'

        elif (search(patterns.pattern_562, ani)
                and not search(patterns.pattern_800, dialed_number)):
            return 'activado'

        elif search(patterns.pattern_4469v2, dialed_number):
            return 'activado'

        else:
            return 'desactivado'

    def get_activado_entel(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if search(patterns.pattern_0234469v2, dialed_number):
            return 'activado'

        elif (search(patterns.pattern_64469, dialed_number) and
                not search(patterns.pattern_112, dialed_number)):
            return 'activado'

        else:
            return 'desactivado'

    def get_zona_rango(self, ani):
        """Retorna la zona y rango del ani_number"""
        if search(patterns.pattern_569, ani):
            return ani[2:][:1], ani[3:][:4]

        elif search(patterns.pattern_9, ani):
            return ani[2:][:2], ani[4:][:4]

        elif search(patterns.pattern_562, ani):
            return ani[2:][:1], ani[3:][:5]

        else:
            return ani[2:][:2], ani[4:][:3]

    def get_compania(self, ani):
        """Funcion que retorna la compañia del numero de origen"""
        portado = Portados.objects.filter(numero=ani).first()

        if portado is not None:
            return portado.compania

        else:
            zona, rango = self.get_zona_rango(ani)
            numeracion = Numeracion.objects.filter(
                zona=zona, rango=rango).first()

            if numeracion is not None:
                return numeracion.compania

            else:
                return None

    def get_tipo(self, ani, final_number):
        """Funcion que determina el tipo de llamada"""
        if search(patterns.pattern_564469, final_number):
            if search(patterns.pattern_569, ani):
                return 'voip-movil'

            elif not search(patterns.pattern_56, ani):
                return 'voip-ldi'

            else:
                return 'voip-local'

        else:
            if search(patterns.pattern_569, ani):
                return 'movil'

            elif not search(patterns.pattern_56, ani):
                return 'internacional'

            elif search(patterns.pattern_562, ani):
                return 'local'

            elif search(patterns.pattern_5610, ani):
                return 'especial'

            else:
                return 'nacional'

    def get_dia(self, fecha):
        feriado = Feriado.objects.filter(fecha=fecha).first()

        if feriado is not None:
            return "festivo"

        else:
            if fecha.weekday() in range(5):
                return "habil"

            elif fecha.weekday() == 5:
                return "sabado"

            else:
                return "festivo"

    def horario_compania(self, fecha_llamada, hora_llamada, compania):
        dia = self.get_dia(fecha_llamada)
        normal = Horario.objects.filter(
            compania=compania, dia=dia, tipo='normal').first()
        reducido = Horario.objects.filter(
            compania=compania, dia=dia, tipo='reducido').first()
        nocturno = Horario.objects.filter(
            compania=compania, dia=dia, tipo='nocturno').first()

        if normal:
            if normal.inicio < normal.fin:
                if normal.inicio <= hora_llamada <= normal.fin:
                    return "normal"
            else:
                if normal.inicio <= hora_llamada <= dt.time(23, 59, 59):
                    return "normal"
                elif dt.time(0, 0) <= hora_llamada <= normal.fin:
                    return "normal"

        if reducido:
            if reducido.inicio < reducido.fin:
                if reducido.inicio <= hora_llamada <= reducido.fin:
                    return "reducido"
            else:
                if reducido.inicio <= hora_llamada <= dt.time(23, 59, 59):
                    return "reducido"
                elif dt.time(0, 0) <= hora_llamada <= reducido.fin:
                    return "reducido"

        if nocturno:
            if nocturno.inicio < nocturno.fin:
                if nocturno.inicio <= hora_llamada <= nocturno.fin:
                    return "nocturno"
            else:
                if nocturno.inicio <= hora_llamada <= dt.time(23, 59, 59):
                    return "nocturno"
                elif dt.time(0, 0) <= hora_llamada <= nocturno.fin:
                    return "nocturno"

    def split_horario(self, connect_time, duracion, compania):
        fecha_llamada = connect_time.date()
        dia = self.get_dia(fecha_llamada)
        normal = Horario.objects.filter(
            compania=compania, dia=dia, tipo='normal').first()
        reducido = Horario.objects.filter(
            compania=compania, dia=dia, tipo='reducido').first()
        nocturno = Horario.objects.filter(
            compania=compania, dia=dia, tipo='nocturno').first()
        hora_inicio = nptime().from_time(connect_time.time())
        hora_fin = hora_inicio + dt.timedelta(seconds=float(duracion))

        if hora_inicio <= hora_fin:
            if normal:
                if hora_inicio < normal.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    normal.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal.inicio
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal.inicio)
                            ).total_seconds())
                        },
                    )
                elif hora_inicio < normal.fin < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(normal.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal.fin)
                            ).total_seconds())
                        },
                    )
            if reducido:
                if hora_inicio < reducido.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido.inicio
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                reducido.inicio)
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < reducido.fin < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(reducido.fin)
                            ).total_seconds())
                        },
                    )
            if nocturno:
                if hora_inicio < nocturno.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno.inicio
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                nocturno.inicio)
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < nocturno.fin < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(nocturno.fin)
                            ).total_seconds())
                        },
                    )
            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion,
                },
            )
        else:
            if normal:
                if hora_inicio < normal.inicio < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    normal.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal.inicio
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    normal.inicio)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < normal.fin < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(normal.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    normal.fin)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < normal.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    normal.inicio) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                normal.inicio
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal.inicio)
                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= normal.fin <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    normal.fin) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                normal.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal.fin)
                            ).total_seconds())
                        },
                    )
            if reducido:
                if hora_inicio < reducido.inicio < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido.inicio
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    reducido.inicio)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < reducido.fin < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    reducido.fin)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < reducido.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    reducido.inicio) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                reducido.inicio
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                reducido.inicio)
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= reducido.fin <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    reducido.fin) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                reducido.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(reducido.fin)
                            ).total_seconds())
                        },
                    )
            if nocturno:
                if hora_inicio < nocturno.inicio < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.inicio) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno.inicio
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    nocturno.inicio)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < nocturno.fin < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.fin) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    nocturno.fin)
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < nocturno.inicio < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.inicio) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                nocturno.inicio
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                nocturno.inicio)
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= nocturno.fin <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    nocturno.fin) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                nocturno.fin) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(nocturno.fin)
                            ).total_seconds())
                        },
                    )

            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion
                },
            )

    def get_entity(self, dialed_number):
        if len(dialed_number) == 8 and dialed_number[0] == '2':
            numero = int('562' + dialed_number)

        else:
            numero = int('56' + dialed_number)

        linea = Lineas.objects.filter(numero=numero).first()

        return None if linea is None else linea.numero

    def cargar_cdr(self):
        logs = []

        if self.compania == 'CTC':
            get_activado = self.get_activado_ctc

        elif self.compania == 'ENTEL':
            get_activado = self.get_activado_entel

        if self.source:
            lines = [
                r.split(',') for r in self.source.read().split('\r\n')[:-1]]
            head = lines[0]

            for line in lines[1:]:
                row = dict(zip(head, line))
                observacion = ''

                if self.valida_ani(row['ANI']):
                    activado = get_activado(
                        row['ANI'], row['DIALED_NUMBER'])

                else:
                    activado = 'desactivado'
                    observacion = 'ani invalido'

                if activado == 'activado':
                    compania_ani_number = self.get_compania(row['ANI'])

                    if compania_ani_number is None:
                        activado = 'desactivado'
                        observacion = 'ani_number sin numeracion'

                    tipo = self.get_tipo(row['ANI'], row['DIALED_NUMBER'])

                else:
                    compania_ani_number = None
                    tipo = None
                    observacion = 'No cumple con los filtros'

                ani_number = int(row['ANI_NUMBER']) if row[
                    'ANI_NUMBER'].isdigit() else None
                ingress_duration = int(row['INGRESS_DURATION']) if row[
                    'INGRESS_DURATION'].isdigit() else None
                is_digit = row['DIALED_NUMBER'].isdigit()
                length = len(row['DIALED_NUMBER']) < 20
                entity = self.get_entity(row['DIALED_NUMBER'])
                dialed_number = int(
                    row['DIALED_NUMBER']) if is_digit and length else None
                connect_time = dt.datetime.strptime(
                    row['CONNECT_TIME'], '%Y-%m-%d %H:%M:%S')

                if activado == 'activado':
                    for rango in self.split_horario(
                            connect_time, ingress_duration,
                            compania_ani_number):
                        fecha_llamada = rango['fecha_llamada']

                        if str(fecha_llamada.month) != self.month:
                            fecha_llamada = connect_time.date()

                        hora_llamada = rango['hora_inicio']
                        horario = self.horario_compania(
                            fecha_llamada, hora_llamada, compania_ani_number)
                        duracion = rango['duracion']
                        connect_time2 = dt.datetime.combine(
                            fecha_llamada, hora_llamada)
                        logs.append(
                            LogLlamadas(
                                connect_time=connect_time2,
                                ani_number=ani_number,
                                ingress_duration=duracion,
                                dialed_number=dialed_number,
                                fecha=self.fecha,
                                compania_cdr=self.compania,
                                estado=activado,
                                motivo=observacion,
                                compania_ani=compania_ani_number,
                                tipo=tipo,
                                hora=hora_llamada,
                                date=fecha_llamada,
                                horario=horario,
                                entity=entity
                            )
                        )

                else:
                    logs.append(
                        LogLlamadas(
                            connect_time=connect_time,
                            ani_number=ani_number,
                            ingress_duration=ingress_duration,
                            dialed_number=dialed_number,
                            fecha=self.fecha,
                            compania_cdr=self.compania,
                            estado=activado,
                            motivo=observacion,
                            compania_ani=compania_ani_number,
                            tipo=tipo,
                            hora=connect_time.time(),
                            date=connect_time.date(),
                            horario='',
                            entity=entity
                        )
                    )

            LogLlamadas.objects.bulk_create(logs)

            return True

        return False

    def save(self, *args, **kwargs):
        if self.id is None:
            self.fecha = '{0}-{1}'.format(self.year, self. month)

        super(Cdr, self).save(*args, **kwargs)

    @classmethod
    def processes(cls):
        results = []

        for cdr in cls.objects.filter(processed=False).exclude(
                source__isnull=True):
            result = cdr.cargar_cdr()
            result = 'Procesado' if result else 'Ocurrio un error'
            results.append('{0}: {1}'.format(cdr.compania, result))

        return '\n'.join(results)


class Compania(models.Model):
    id_compania = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=255, blank=True)
    entidad = models.CharField(max_length=255, blank=True)
    id = models.IntegerField(blank=True, null=True)
    codigo = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'compania'
        verbose_name = 'compania'
        verbose_name_plural = 'companias'
        ordering = ('nombre',)

    def __unicode__(self):
        return self.nombre


class DetFactura(models.Model):
    HORARIOS = (
        ('normal', 'normal'),
        ('reducido', 'reducido'),
        ('nocturno', 'nocturno'),
    )
    id_detalle = models.AutoField(primary_key=True)
    origen = models.IntegerField()
    destino = models.IntegerField()
    fecha = models.DateField()
    hora = models.CharField(max_length=255)
    duracion = models.FloatField()
    tarifa = models.ForeignKey('Tarifa', db_column='tarifa')
    horario = models.CharField(max_length=255, choices=HORARIOS)
    valor = models.FloatField()
    compania = models.ForeignKey(Compania, db_column='compania')
    factura = models.ForeignKey('Factura', db_column='factura')

    class Meta:
        db_table = 'det_factura'
        verbose_name = 'detalle de factura'
        verbose_name_plural = 'detalle de facturas'

    def __unicode__(self):
        return u'{0} {1}'.format(self.fecha, self.hora)


class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    compania = models.ForeignKey(Compania, db_column='compania')
    fecha_inicio = ArrayField(dbtype="date", blank=True)
    fecha_fin = ArrayField(dbtype="date", blank=True)
    tarifa = ArrayField(dbtype="int", blank=True)
    valor_normal = ArrayField(dbtype="float", blank=True)
    valor_reducido = ArrayField(dbtype="float", blank=True)
    valor_nocturno = ArrayField(dbtype="float", blank=True)
    usuario = models.ForeignKey('Usuarios', db_column='usuario', default=38)
    month = models.CharField(
        max_length=2, choices=choices.MONTHS, default='', blank=True)
    year = models.CharField(
        max_length=4, choices=choices.YEARS, default='', blank=True)
    valor_total = models.FloatField(null=True, blank=True, default=None)
    total_llamadas = models.IntegerField(null=True, blank=True, default=None)
    total_segundos = models.IntegerField(null=True, blank=True, default=None)

    class Meta:
        db_table = 'factura'
        ordering = ('-pk',)
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'

    def __unicode__(self):
        return u'{0}-{1} {2}'.format(self.year, self.month, self.compania)

    def resumenes(self):
        return self.resumenfactura_set.all()

    def get_horarios(self):
        horario = {
            'habil': {
                'normal': {},
                'reducido': {},
                'nocturno': {}},
            'sabado': {
                'normal': {},
                'reducido': {},
                'nocturno': {}},
            'festivo': {
                'normal': {},
                'reducido': {},
                'nocturno': {}}}

        resultados = Horario.objects.filter(compania=self.compania).exclude(
            inicio__isnull=True)

        for r in resultados:
            horario[r.dia][r.tipo]['inicio'] = r.inicio
            horario[r.dia][r.tipo]['fin'] = r.fin

        return horario

    def get_tarifas(self):
        tarifas = {}
        resultados = Tarifa.objects.filter(compania=self.compania)

        for r in resultados:
            tarifas[r.fecha] = {}
            tarifas[r.fecha] = {}
            tarifas[r.fecha] = {}
            tarifas[r.fecha] = {}

        for r in resultados:
            tarifas[r.fecha]['id_tarifa'] = r.id_tarifa
            tarifas[r.fecha]['valor_normal'] = r.valor_normal
            tarifas[r.fecha]['valor_reducido'] = r.valor_reducido
            tarifas[r.fecha]['valor_nocturno'] = r.valor_nocturno

        return tarifas

    def horario_compania(self, dia, hora_llamada, horarios):
        normal = horarios[dia]['normal']
        reducido = horarios[dia]['reducido']
        nocturno = horarios[dia]['nocturno']

        if len(normal) > 0:
            if normal['inicio'] < normal['fin']:
                if normal['inicio'] <= hora_llamada <= normal['fin']:
                    return "normal"
            else:
                if normal['inicio'] <= hora_llamada <= dt.time(23, 59, 59):
                    return "normal"
                elif dt.time(0, 0) <= hora_llamada <= normal['fin']:
                    return "normal"

        if len(reducido) > 0:
            if reducido['inicio'] < reducido['fin']:
                if reducido['inicio'] <= hora_llamada <= reducido['fin']:
                    return "reducido"
            else:
                if reducido['inicio'] <= hora_llamada <= dt.time(23, 59, 59):
                    return "reducido"
                elif dt.time(0, 0) <= hora_llamada <= reducido['fin']:
                    return "reducido"

        if len(nocturno) > 0:
            if nocturno['inicio'] < nocturno['fin']:
                if nocturno['inicio'] <= hora_llamada <= nocturno['fin']:
                    return "nocturno"
            else:
                if nocturno['inicio'] <= hora_llamada <= dt.time(23, 59, 59):
                    return "nocturno"
                elif dt.time(0, 0) <= hora_llamada <= nocturno['fin']:
                    return "nocturno"

    def split_horario(
            self, dia, hora_llamada, duracion, fecha_llamada, horarios):
        normal = horarios[dia]['normal']
        reducido = horarios[dia]['reducido']
        nocturno = horarios[dia]['nocturno']
        hora_inicio = nptime().from_time(hora_llamada)
        hora_fin = hora_inicio + dt.timedelta(seconds=float(duracion))

        if hora_inicio <= hora_fin:
            if len(normal) > 0:
                if hora_inicio < normal['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    normal['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal['inicio']
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal['inicio'])
                            ).total_seconds())
                        },
                    )
                elif hora_inicio < normal['fin'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(normal['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal['fin'])
                            ).total_seconds())
                        },
                    )
            if len(reducido) > 0:
                if hora_inicio < reducido['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido['inicio']
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                reducido['inicio'])
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < reducido['fin'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(reducido['fin'])
                            ).total_seconds())
                        },
                    )
            if len(nocturno) > 0:
                if hora_inicio < nocturno['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno['inicio']
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                nocturno['inicio'])
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < nocturno['fin'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(nocturno['fin'])
                            ).total_seconds())
                        },
                    )
            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion,
                },
            )
        else:
            if len(normal) > 0:
                if hora_inicio < normal['inicio'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    normal['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal['inicio']
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    normal['inicio'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < normal['fin'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(normal['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                normal['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    normal['fin'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < normal['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    normal['inicio']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                normal['inicio']
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal['inicio'])
                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= normal['fin'] <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    normal['fin']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                normal['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(normal['fin'])
                            ).total_seconds())
                        },
                    )
            if len(reducido) > 0:
                if hora_inicio < reducido['inicio'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido['inicio']
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    reducido['inicio'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < reducido['fin'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    reducido['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                reducido['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    reducido['fin'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < reducido['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    reducido['inicio']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                reducido['inicio']
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                reducido['inicio'])
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= reducido['fin'] <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    reducido['fin']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                reducido['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(reducido['fin'])
                            ).total_seconds())
                        },
                    )
            if len(nocturno) > 0:
                if hora_inicio < nocturno['inicio'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['inicio']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno['inicio']
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    nocturno['inicio'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < nocturno['fin'] < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['fin']) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                nocturno['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    nocturno['fin'])
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < nocturno['inicio'] < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['inicio']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                nocturno['inicio']
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                nocturno['inicio'])
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= nocturno['fin'] <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    nocturno['fin']) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                nocturno['fin']) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(nocturno['fin'])
                            ).total_seconds())
                        },
                    )

            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion
                },
            )

    def cantidad_tarifa(self):
        return Tarifa.objects.filter(
            fecha__year=self.year, fecha__month=self.month,
            compania=self.compania).count()

    def cantidad_det_factura(self):
        return DetFactura.objects.filter(
            compania=self.compania, fecha__year=self.year,
            fecha__month=self.month).count()

    def get_log_llamadas(self):
        fecha = '{0}-{1}'.format(self.year, self.month)

        return LogLlamadas.objects.filter(
            compania_ani=str(self.compania.id_compania), fecha=fecha,
            estado='activado')

    def get_feriados(self):
        return Feriado.objects.values_list('fecha', flat=True)

    def get_dia(self, fecha, dia, feriados):
        if fecha in feriados:
            dia = "festivo"

        else:
            if dia > 0 and dia < 6:
                dia = "habil"

            if dia == 6:
                dia = "sabado"

            if dia == 7:
                dia = "festivo"

        return dia

    def update_logs(self):
        """Funcion que guarda en la base dedatos el log de llamadas"""
        fecha = '{0}-{1}'.format(self.year, self.month)
        LogLlamadas.objects.filter(
            compania_ani=str(self.compania.id_compania), fecha=fecha,
            estado='activado').update(estado='facturado')

    def update_factura(self):
        fechas_inicio = []
        fechas_fin = []
        tarifas = []
        valores_normales = []
        valores_reducidos = []
        valores_nocturnos = []
        limites = Tarifa.objects.filter(
            compania=self.compania, fecha__year=self.year,
            fecha__month=self.month
        ).distinct(
            'id_ingreso', 'valor_normal', 'valor_reducido',
            'valor_nocturno')

        for limite in limites:
            fechas = Tarifa.objects.filter(id_ingreso=limite.id_ingreso)
            fecha_inicio = fechas.aggregate(Min('fecha')).get('fecha__min')
            fechas_inicio.append(fecha_inicio)
            fecha_fin = fechas.aggregate(Max('fecha')).get('fecha__max')
            fechas_fin.append(fecha_fin)
            tarifa = fechas.aggregate(Min('id_tarifa')).get('id_tarifa__min')
            tarifas.append(tarifa)
            tarifa = Tarifa.objects.get(pk=tarifa)
            valores = self.detfactura_set.filter(
                horario__startswith='normal',
                fecha__range=(fecha_inicio, fecha_fin))
            valor_normal = valores.aggregate(Sum('valor')).get('valor__sum')
            valores_normales.append(valor_normal)
            duracion_normal = valores.aggregate(
                Sum('duracion')).get('duracion__sum')

            valores = self.detfactura_set.filter(
                horario__startswith='reducido',
                fecha__range=(fecha_inicio, fecha_fin))
            valor_reducido = valores.aggregate(Sum('valor')).get('valor__sum')
            valores_reducidos.append(valor_reducido)
            duracion_reducido = valores.aggregate(
                Sum('duracion')).get('duracion__sum')

            valores = self.detfactura_set.filter(
                horario__startswith='nocturno',
                fecha__range=(fecha_inicio, fecha_fin))
            valor_nocturno = valores.aggregate(Sum('valor')).get('valor__sum')
            valores_nocturnos.append(valor_nocturno)
            duracion_nocturno = valores.aggregate(
                Sum('duracion')).get('duracion__sum')

            total = valor_normal + valor_reducido + valor_nocturno

            ResumenFactura(
                factura=self,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                duracion_normal=duracion_normal,
                valor_normal=valor_normal,
                tarifa_normal=tarifa.valor_normal,
                duracion_reducido=duracion_reducido,
                valor_reducido=valor_reducido,
                tarifa_reducido=tarifa.valor_reducido,
                duracion_nocturno=duracion_nocturno,
                valor_nocturno=valor_nocturno,
                tarifa_nocturno=tarifa.valor_nocturno,
                total=total).save()

        valor_total = self.detfactura_set.aggregate(
            Sum('valor')).get('valor__sum')
        total_segundos = self.detfactura_set.aggregate(
            Sum('duracion')).get('duracion__sum')
        total_llamadas = self.detfactura_set.count()

        self.fecha_inicio = fechas_inicio
        self.fecha_fin = fechas_fin
        self.tarifa = tarifas
        self.valor_normal = valores_normales
        self.valor_reducido = valores_reducidos
        self.valor_nocturno = valores_nocturnos
        self.valor_total = valor_total
        self.total_llamadas = total_llamadas
        self.total_segundos = total_segundos
        self.save()

    def facturar(self):
        fecha = '{0}-{1}'.format(self.year, self.month)
        calendario = monthrange(int(self.year), int(self.month))
        feriados = self.get_feriados()
        horarios = self.get_horarios()
        tarifas = self.get_tarifas()
        logs = self.get_log_llamadas()

        if (self.cantidad_tarifa() >= calendario[1]
                and self.cantidad_det_factura() == 0
                and logs.count() > 0):
            llamadas = []
            detalles = []

            for log in logs:
                id_llamada = log.id_log
                origen = log.ani_number
                destino = log.dialed_number
                duracion = log.ingress_duration
                fecha_llamada = log.connect_time.date()
                hora_llamada = log.connect_time.time()
                dia = self.get_dia(
                    fecha_llamada, fecha_llamada.isoweekday(), feriados)

                for rango in self.split_horario(
                        dia, hora_llamada, duracion, fecha_llamada, horarios):
                    fecha_llamada2 = rango['fecha_llamada']

                    if str(fecha_llamada2.month) != fecha[-2:]:
                        fecha_llamada2 = fecha_llamada

                    dia2 = self.get_dia(
                        fecha_llamada2, fecha_llamada2.isoweekday(), feriados)
                    horario2 = self.horario_compania(
                        dia2, rango['hora_inicio'], horarios)
                    valor_tarifa = tarifas[fecha_llamada2]['valor_' + horario2]
                    id_tarifa = tarifas[fecha_llamada2]['id_tarifa']
                    duracion2 = rango['duracion']
                    valor_llamada = valor_tarifa * duracion2
                    hora_llamada2 = rango['hora_inicio']
                    detalles.append(
                        DetFactura(
                            origen=origen,
                            destino=destino,
                            fecha=fecha_llamada2,
                            hora=str(hora_llamada2),
                            duracion=duracion2,
                            tarifa=Tarifa.objects.get(pk=id_tarifa),
                            horario=horario2,
                            valor=valor_llamada,
                            compania=self.compania,
                            factura=self
                        )
                    )
                    llamadas.append(id_llamada)

            DetFactura.objects.bulk_create(detalles)
            self.update_logs()
            self.update_factura()

    def reset_logs(self):
        fecha = '{0}-{1}'.format(self.year, self. month)
        LogLlamadas.objects.filter(
            fecha=fecha, estado='facturado',
            compania_ani=self.compania.pk).update(estado='activado')


class Feriado(models.Model):
    id_feriado = models.AutoField(primary_key=True)
    fecha = models.DateField()

    class Meta:
        db_table = 'feriado'
        verbose_name = 'feriado'
        verbose_name_plural = 'feriados'
        ordering = ('-fecha',)

    def __unicode__(self):
        return u'{0}'.format(self.fecha)


class Horario(models.Model):
    DIAS = (
        ('habil', 'habil'),
        ('sabado', 'sabado'),
        ('festivo', 'festivo'),
    )
    TIPOS = (
        ('normal', 'normal'),
        ('reducido', 'reducido'),
        ('nocturno', 'nocturno'),
    )
    id = models.AutoField(primary_key=True)
    dia = models.CharField(max_length=255, choices=DIAS)
    tipo = models.CharField(max_length=255, choices=TIPOS)
    inicio = models.TimeField(blank=True, null=True)
    fin = models.TimeField(blank=True, null=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'horario'
        verbose_name = 'horario'
        verbose_name_plural = 'horarios'

    def __unicode__(self):
        return u'{0} {1}'.format(self.dia, self.tipo)


class Ido(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.IntegerField(unique=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'ido'
        verbose_name = 'ido'
        verbose_name_plural = 'idos'
        ordering = ('codigo',)

    def __unicode__(self):
        return u'{0}'.format(self.codigo)


class LogLlamadas(models.Model):
    COMPANIA_CDRS = (
        ('ENTEL', 'ENTEL'),
        ('CTC', 'CTC'),
    )
    ESTADOS = (
        ('desactivado', 'desactivado'),
        ('activado', 'activado'),
        ('facturado', 'facturado'),
    )
    id_log = models.AutoField(primary_key=True)
    connect_time = models.DateTimeField(blank=True, null=True)
    ani_number = models.CharField(max_length=255, blank=True)
    ingress_duration = models.FloatField(blank=True, null=True)
    dialed_number = models.CharField(max_length=255, blank=True)
    fecha = models.CharField(max_length=7, blank=True)
    compania_cdr = models.CharField(
        max_length=255, blank=True, choices=COMPANIA_CDRS)
    estado = models.CharField(max_length=255, blank=True, choices=ESTADOS)
    motivo = models.CharField(max_length=255, blank=True)
    compania_ani = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    hora = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'log_llamadas'
        verbose_name = 'registro de llamada'
        verbose_name_plural = 'registro de llamadas'

    def __unicode__(self):
        return u'{0} {1}'.format(self.date, self.hora)


class Numeracion(models.Model):
    id = models.AutoField(primary_key=True)
    zona = models.IntegerField()
    rango = models.IntegerField()
    tipo = models.CharField(max_length=255, blank=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'numeracion'
        verbose_name = 'numeracion'
        verbose_name_plural = 'numeraciones'

    def __unicode__(self):
        return u'{0}{1}'.format(self.zona, self.rango)


class NumeracionAmpliada(models.Model):
    id_numeracion = models.AutoField(primary_key=True)
    codigo = models.IntegerField()
    numeracion = models.CharField(max_length=255)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'numeracion_ampliada'
        verbose_name = 'numeracion ampliada'
        verbose_name_plural = 'numeraciones ampliadas'

    def __unicode__(self):
        return u'{0}{1}'.format(self.codigo, self.numeracion)


class Portados(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.IntegerField(unique=True)
    ido = models.IntegerField()
    tipo = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'portados'
        verbose_name = 'portado'
        verbose_name_plural = 'portados'

    def __unicode__(self):
        return u'{0}'.format(self.numero)


class Tarifa(models.Model):
    TIPOS = (
        ('habil', 'habil'),
        ('sabado', 'sabado'),
        ('festivo', 'festivo'),
    )
    id_tarifa = models.AutoField(primary_key=True)
    compania = models.ForeignKey(Compania, db_column='compania')
    fecha = models.DateField()
    valor_normal = models.FloatField()
    valor_reducido = models.FloatField()
    valor_nocturno = models.FloatField()
    tipo = models.CharField(max_length=255, blank=True, choices=TIPOS)
    id_ingreso = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'tarifa'
        verbose_name = 'tarifa'
        verbose_name_plural = 'tarifas'

    def __unicode__(self):
        return self.tipo

    @classmethod
    def get_next_id_ingreso(cls):
        cursor = connection.cursor()
        cursor.execute("SELECT nextval(%s)", ['sec_tarifa_ingreso'])
        row = cursor.fetchone()

        return row[0]

    @classmethod
    def ingress(
            cls, compania, fecha_inicio, fecha_fin, valor_normal,
            valor_reducido, valor_nocturno):
        tarifas = []
        id_ingreso = cls.get_next_id_ingreso()

        for fecha in rrule(DAILY, dtstart=fecha_inicio, until=fecha_fin):
            if cls.objects.filter(fecha=fecha).count() == 0:
                if (fecha.weekday() == 0 or
                        Feriado.objects.filter(fecha=fecha).count() > 0):
                    tipo = 'festivo'

                elif fecha.weekday() in range(1, 6):
                    tipo = 'habil'

                elif fecha.weekday() == 6:
                    tipo = 'sabado'

                tarifas.append(cls(
                    compania=compania,
                    fecha=fecha,
                    valor_normal=valor_normal,
                    valor_reducido=valor_reducido,
                    valor_nocturno=valor_nocturno,
                    tipo=tipo,
                    id_ingreso=id_ingreso
                ))

        cls.objects.bulk_create(tarifas)

    @classmethod
    def get_by_compania_and_fecha(cls, compania, year, month):
        limites = []

        for t in cls.objects.filter(
                compania=compania, fecha__year=year,
                fecha__month=month).distinct('id_ingreso'):
            fechas = cls.objects.filter(id_ingreso=t.id_ingreso)
            fecha_inicio = fechas.aggregate(Min('fecha')).get('fecha__min')
            fecha_fin = fechas.aggregate(Max('fecha')).get('fecha__max')
            limites.append({
                'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin,
                'id_ingreso': t.id_ingreso})

        return limites

    @classmethod
    def get_by_id_ingreso(cls, id_ingreso):
        return cls.objects.filter(id_ingreso=id_ingreso)[0]


class Usuarios(models.Model):
    ROLES = (
        ('Operador', 'Operador'),
        ('Administrador', 'Administrador'),
    )
    id_usuario = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo = models.EmailField(blank=True)
    rol = models.CharField(max_length=255, choices=ROLES)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __unicode__(self):
        return self.usuario

    def get_full_name(self):
        return u'{0} {1}'.format(self.nombre, self.apellido)


class ResumenFactura(models.Model):
    factura = models.ForeignKey(Factura)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion_normal = models.IntegerField()
    duracion_reducido = models.IntegerField()
    duracion_nocturno = models.IntegerField()
    tarifa_normal = models.FloatField()
    tarifa_reducido = models.FloatField()
    tarifa_nocturno = models.FloatField()
    valor_normal = models.FloatField()
    valor_reducido = models.FloatField()
    valor_nocturno = models.FloatField()
    total = models.FloatField()

    class Meta:
        db_table = 'resumen_factura'
        verbose_name = 'resumen factura'
        verbose_name_plural = 'resumenes factura'

    def __unicode__(self):
        return u'Resumen factura {0} desde {1} hasta {2}'.format(
            self.factura.pk, self.fecha_inicio, self.fecha_fin)


class Company(mongoengine.Document):

    """Modelo de compañias."""

    name = mongoengine.StringField(unique=True)
    code = mongoengine.IntField()
    schedules = mongoengine.DictField()

    def __unicode__(self):
        return self.name


class Numeration(mongoengine.Document):

    """Modelo de las numeraciones."""

    zone = mongoengine.IntField()
    _range = mongoengine.IntField()
    company = mongoengine.ReferenceField(Company)

    def __unicode__(self):
        return u'{0}{1}'.format(self.zone, self._range)


class Line(mongoengine.Document):

    """Modelo de los clientes de convergia."""

    number = mongoengine.IntField(unique=True)
    name = mongoengine.StringField()
    entity = mongoengine.StringField(choices=choices.ENTITIES)
    comments = mongoengine.StringField()
    zone = mongoengine.IntField(choices=choices.ZONES)
    city = mongoengine.IntField(choices=choices.CITIES)


class Cdr2(mongoengine.Document):

    """Modelo de los cdr."""

    month = mongoengine.StringField(
        max_length=2, choices=choices.MONTHS)
    year = mongoengine.StringField(
        max_length=4, choices=choices.YEARS)
    incoming_ctc = mongoengine.FileField()
    incoming_entel = mongoengine.FileField()
    outgoing = mongoengine.FileField()
    processed = mongoengine.BooleanField(default=False)

    def valida_ani(self, ani):
        if len(ani) == 11:
            return True

        else:
            return False

    def get_activado_ctc(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if search(patterns.pattern_569, ani):
            return True

        elif (search(patterns.pattern_562, ani)
                and not search(patterns.pattern_800, dialed_number)):
            return True

        elif search(patterns.pattern_4469v2, dialed_number):
            return True

        else:
            return False

    def get_activado_entel(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if search(patterns.pattern_0234469v2, dialed_number):
            return True

        elif (search(patterns.pattern_64469, dialed_number) and
                not search(patterns.pattern_112, dialed_number)):
            return True

        else:
            return False

    def get_zona_rango(self, ani):
        """Retorna la zona y rango del ani_number"""
        if search(patterns.pattern_569, ani):
            return ani[2:][:1], ani[3:][:4]

        elif search(patterns.pattern_9, ani):
            return ani[2:][:2], ani[4:][:4]

        elif search(patterns.pattern_562, ani):
            return ani[2:][:1], ani[3:][:5]

        else:
            return ani[2:][:2], ani[4:][:3]

    def get_compania(self, ani):
        """Funcion que retorna la compañia del numero de origen"""
        portado = Portability.objects.filter(number=ani).first()

        if portado is not None:
            return portado.company

        else:
            zona, rango = self.get_zona_rango(ani)
            numeracion = Numeration.objects.filter(
                zone=zona, _range=rango).first()

            if numeracion is not None:
                return numeracion.company

            else:
                return None

    def get_tipo(self, ani, final_number):
        """Funcion que determina el tipo de llamada"""
        if search(patterns.pattern_564469, final_number):
            if search(patterns.pattern_569, ani):
                return 'voip-movil'

            elif not search(patterns.pattern_56, ani):
                return 'voip-ldi'

            else:
                return 'voip-local'

        else:
            if search(patterns.pattern_569, ani):
                return 'movil'

            elif not search(patterns.pattern_56, ani):
                return 'internacional'

            elif search(patterns.pattern_562, ani):
                return 'local'

            elif search(patterns.pattern_5610, ani):
                return 'especial'

            else:
                return 'nacional'

    def get_dia(self, fecha):
        feriado = Holiday.objects.filter(date=fecha).first()

        if feriado is not None:
            return 'festivo'

        else:
            if fecha.weekday() in range(5):
                return 'habil'

            elif fecha.weekday() == 5:
                return 'sabado'

            else:
                return 'festivo'

    def horario_compania(self, fecha_llamada, hora_llamada, compania):
        dia = self.get_dia(fecha_llamada)
        normal = compania.schedules.get(dia)
        if normal:
            normal = normal.get('normal')
        reducido = compania.schedules.get(dia)
        if reducido:
            reducido = reducido.get('reducido')
        nocturno = compania.schedules.get(dia)
        if nocturno:
            nocturno = nocturno.get('nocturno')

        if normal:
            if dt.datetime.strptime(normal['start'],'%H:%M:%S').time() < dt.datetime.strptime(normal['end'],'%H:%M:%S').time():
                if dt.datetime.strptime(normal['start'],'%H:%M:%S').time() <= hora_llamada <= dt.datetime.strptime(normal['end'],'%H:%M:%S').time():
                    return 'normal'
            else:
                if dt.datetime.strptime(normal['start'],'%H:%M:%S').time() <= hora_llamada <= dt.time(23, 59, 59):
                    return 'normal'
                elif dt.time(0, 0) <= hora_llamada <= dt.datetime.strptime(normal['end'],'%H:%M:%S').time():
                    return 'normal'

        if reducido:
            if dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() < dt.datetime.strptime(reducido['end'],'%H:%M:%S').time():
                if dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() <= hora_llamada <= dt.datetime.strptime(reducido['end'],'%H:%M:%S').time():
                    return 'reducido'
            else:
                if dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() <= hora_llamada <= dt.time(23, 59, 59):
                    return 'reducido'
                elif dt.time(0, 0) <= hora_llamada <= dt.datetime.strptime(reducido['end'],'%H:%M:%S').time():
                    return 'reducido'

        if nocturno:
            if dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() < dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time():
                if dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() <= hora_llamada <= dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time():
                    return 'nocturno'
            else:
                if dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() <= hora_llamada <= dt.time(23, 59, 59):
                    return 'nocturno'
                elif dt.time(0, 0) <= hora_llamada <= dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time():
                    return 'nocturno'

    def split_horario(self, connect_time, duracion, compania):
        fecha_llamada = connect_time.date()
        dia = self.get_dia(fecha_llamada)
        normal = compania.schedules.get(dia)
        if normal:
            normal = normal.get('normal')
        reducido = compania.schedules.get(dia)
        if reducido:
            reducido = reducido.get('reducido')
        nocturno = compania.schedules.get(dia)
        if nocturno:
            nocturno = nocturno.get('nocturno')
        hora_inicio = nptime().from_time(connect_time.time())
        hora_fin = hora_inicio + dt.timedelta(seconds=float(duracion))

        if hora_inicio <= hora_fin:
            if normal:
                if hora_inicio < dt.datetime.strptime(normal['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(normal['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(normal['start'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
                elif hora_inicio < dt.datetime.strptime(normal['end'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(normal['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
            if reducido:
                if hora_inicio < dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                dt.datetime.strptime(reducido['start'],'%H:%M:%S').time())
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < dt.datetime.strptime(reducido['end'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(reducido['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
            if nocturno:
                if hora_inicio < dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time())
                                            ).total_seconds())
                        },
                    )
                elif hora_inicio < dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion,
                },
            )
        else:
            if normal:
                if hora_inicio < dt.datetime.strptime(normal['start'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(normal['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(normal['start'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < dt.datetime.strptime(normal['end'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(normal['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < dt.datetime.strptime(normal['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(normal['start'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(normal['start'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= dt.datetime.strptime(normal['end'],'%H:%M:%S').time() <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(normal['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(normal['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
            if reducido:
                if hora_inicio < dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(reducido['start'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < dt.datetime.strptime(reducido['end'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(reducido['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < dt.datetime.strptime(reducido['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                dt.datetime.strptime(reducido['start'],'%H:%M:%S').time())
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= dt.datetime.strptime(reducido['end'],'%H:%M:%S').time() <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(reducido['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(reducido['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )
            if nocturno:
                if hora_inicio < dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )
                elif hora_inicio < dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time() < dt.time(23, 59, 59):
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                nptime(23, 59, 59) - nptime().from_time(
                                    dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                hora_fin - nptime(0, 0)
                            ).total_seconds()) + 1
                        }
                    )

                elif dt.time(0, 0) < dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time() < hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time()
                            ),
                            'duracion': int((
                                hora_fin -
                                            nptime().from_time(
                                                dt.datetime.strptime(nocturno['start'],'%H:%M:%S').time())
                                            ).total_seconds())
                        },
                    )
                elif dt.time(0, 0) <= dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time() <= hora_fin:
                    return (
                        {
                            'fecha_llamada': fecha_llamada,
                            'hora_inicio': hora_inicio,
                            'duracion': int((
                                nptime(23, 59, 59) - hora_inicio
                            ).total_seconds())
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime(0, 0),
                            'duracion': int((
                                nptime().from_time(
                                    dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) - nptime(0, 0)
                            ).total_seconds()) + 1
                        },
                        {
                            'fecha_llamada': fecha_llamada + dt.timedelta(
                                days=1),
                            'hora_inicio': nptime().from_time(
                                dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time()) + dt.timedelta(seconds=1),
                            'duracion': int((
                                hora_fin - nptime().from_time(dt.datetime.strptime(nocturno['end'],'%H:%M:%S').time())
                            ).total_seconds())
                        },
                    )

            return (
                {
                    'fecha_llamada': fecha_llamada,
                    'hora_inicio': hora_inicio,
                    'duracion': duracion
                },
            )

    def get_entity(self, dialed_number):
        if len(dialed_number) == 8 and dialed_number[0] == '2':
            numero = int('562' + dialed_number)

        else:
            numero = int('56' + dialed_number)
        linea = Line.objects.filter(number=numero).first()

        return None if linea is None else linea.entity

    def insert_incoming(self, name):
        incomings = []
        if name == 'ENTEL':
            lines = [
                r.split(',')
                for r in self.incoming_entel.read().decode().split('\r\n')[:-1]]
            get_activado = self.get_activado_entel

        else:
            lines = [
                r.split(',')
                for r in self.incoming_ctc.read().decode().split('\r\n')[:-1]]
            get_activado = self.get_activado_ctc

        head = lines[0]

        for line in lines[1:]:
            row = dict(zip(head, line))
            observation = None

            if self.valida_ani(row['ANI']):
                valid = get_activado(
                    row['ANI'], row['DIALED_NUMBER'])

            else:
                valid = False
                observation = 'ani invalido'

            if valid:
                company = self.get_compania(row['ANI'])

                if company is None:
                    valid = False
                    observation = 'ani_number sin numeracion'
                    tipo = None
                    entity = None

                else:
                    tipo = self.get_tipo(row['ANI'], row['DIALED_NUMBER'])
                    entity = self.get_entity(row['DIALED_NUMBER'])

            else:
                company = None
                tipo = None
                entity = None
                observation = 'No cumple con los filtros'

            ani_number = int(row['ANI_NUMBER']) if row[
                'ANI_NUMBER'].isdigit() else None
            ingress_duration = int(row['INGRESS_DURATION']) if row[
                'INGRESS_DURATION'].isdigit() else None
            is_digit = row['DIALED_NUMBER'].isdigit()
            length = len(row['DIALED_NUMBER']) < 20
            dialed_number = int(
                row['DIALED_NUMBER']) if is_digit and length else None
            connect_time = dt.datetime.strptime(
                row['CONNECT_TIME'], '%Y-%m-%d %H:%M:%S')

            if valid and ingress_duration is not None:
                for rango in self.split_horario(
                        connect_time, ingress_duration,
                        company):
                    fecha_llamada = rango['fecha_llamada']

                    if str(fecha_llamada.month) != self.month:
                        fecha_llamada = connect_time.date()

                    hora_llamada = rango['hora_inicio']
                    horario = self.horario_compania(
                        fecha_llamada, hora_llamada, company)
                    duracion = rango['duracion']
                    connect_time2 = dt.datetime.combine(
                        fecha_llamada, hora_llamada)
                    incomings.append(Incoming(
                        connect_time=connect_time2,
                        ani_number=ani_number,
                        ingress_duration=duracion,
                        dialed_number=dialed_number,
                        cdr=self,
                        valid=valid,
                        observation=observation,
                        company=company,
                        _type=tipo,
                        schedule=horario,
                        entity=entity
                    ))

            else:
                incomings.append(Incoming(
                    connect_time=connect_time,
                    ani_number=ani_number,
                    ingress_duration=ingress_duration,
                    dialed_number=dialed_number,
                    cdr=self,
                    valid=valid,
                    observation=observation,
                    company=company,
                    _type=tipo,
                    entity=entity
                ))

        print('Insertando registros')
        Incoming.objects.insert(incomings)

        return True


class Incoming(mongoengine.Document):

    """Modelo de las llamdas entrantes."""

    connect_time = mongoengine.DateTimeField()
    ani_number = mongoengine.IntField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.IntField()
    cdr = mongoengine.ReferenceField(Cdr2)
    valid = mongoengine.BooleanField()
    invoiced = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)
    _type = mongoengine.StringField(choices=choices.TIPOS)
    entity = mongoengine.StringField(choices=choices.ENTITIES)


class Outgoing(mongoengine.Document):

    """Modelo de las llamdas salientes."""

    connect_time = mongoengine.DateTimeField()
    ani_number = mongoengine.IntField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.IntField()
    cdr = mongoengine.ReferenceField(Cdr2)
    valid = mongoengine.BooleanField()
    invoiced = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)


class Portability(mongoengine.Document):

    """Modelo de los numeros portados."""

    number = mongoengine.IntField(unique=True)
    company = mongoengine.ReferenceField(Company)
    date = mongoengine.DateTimeField()


class Holiday(mongoengine.Document):

    """Modelo de los feriados."""

    date = mongoengine.DateTimeField(unique=True)
