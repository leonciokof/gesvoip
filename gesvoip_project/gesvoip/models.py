# -*- coding: utf-8 -*-

from calendar import monthrange
from re import search
import datetime as dt

from django.db import models
from django.db.models import Max, Min, Sum

from djorm_pgarray.fields import ArrayField
from nptime import nptime

from . import choices, patterns


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
        if (search(patterns.pattern_zonas1, ani) and len(ani) == 11 or
                search(patterns.pattern_zonas2, ani) and len(ani) == 10):
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

        elif search(patterns.pattern_4469, dialed_number):
            return True

        elif search(patterns.pattern_04469, dialed_number):
            return True

        elif search(patterns.pattern_64469, dialed_number):
            return True

        else:
            return False

    def get_activado_entel(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if search(patterns.pattern_0234469, dialed_number):
            return True

        elif search(patterns.pattern_4469, dialed_number):
            return True

        elif (search(patterns.pattern_64469, dialed_number) and
                not search(patterns.pattern_112, dialed_number)):
            return True

        else:
            return False

    def get_zona_rango(self, ani):
        """Funcion que determina el IDO de un ANI"""
        if search(patterns.pattern_569, ani):
            return ani[2:][:1], ani[3:][:4]

        elif search(patterns.pattern_92, ani):
            return ani[2:][:2], ani[4:][:4]

        elif search(patterns.pattern_93, ani) and len(ani) == 11:
            return ani[2:][:2], ani[4:][:4]

        elif search(patterns.pattern_93, ani) and len(ani) == 10:
            return ani[2:][:2], ani[4:][:3]

        elif search(patterns.pattern_562, ani) and len(ani) == 11:
            return ani[2:][:1], ani[3:][:5]

        else:
            return ani[2:][:2], ani[4:][:3]

    def get_compania(self, zona, rango, ani, portados, numeracion):
        """Funcion que retorna la compañia del numero de origen"""
        numero = u'{0}{1}'.format(zona, rango)

        if int(ani) in portados:
            return portados[int(ani)]

        elif numero in numeracion:
            return numeracion[numero]

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

    def cargar_cdr(self):
        logs = []
        portados = {
            p.numero: Ido.objects.get(codigo=p.ido).compania.id_compania
            for p in Portados.objects.all()}
        numeracion = {
            n.__unicode__(): n.compania.id_compania
            for n in Numeracion.objects.all()}

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
                    activado = False
                    observacion = 'ani invalido'

                if activado:
                    zona, rango = self.get_zona_rango(row['ANI'])
                    compania_ani_number = self.get_compania(
                        zona, rango, row['ANI'], portados, numeracion)

                    if compania_ani_number is None:
                        activado = False
                        observacion = 'ani_number sin numeracion'

                    tipo = self.get_tipo(row['ANI'], row['DIALED_NUMBER'])

                else:
                    compania_ani_number = None
                    tipo = None
                    observacion = 'No cumple con los filtros'

                activado = 'activado' if activado else 'desactivado'
                ani_number = int(row['ANI_NUMBER']) if row[
                    'ANI_NUMBER'].isdigit() else None
                ingress_duration = int(row['INGRESS_DURATION']) if row[
                    'INGRESS_DURATION'].isdigit() else None
                is_digit = row['DIALED_NUMBER'].isdigit()
                length = len(row['DIALED_NUMBER']) < 20
                dialed_number = int(
                    row['DIALED_NUMBER']) if is_digit and length else None
                logs.append(
                    LogLlamadas(
                        connect_time=dt.datetime.strptime(
                            row['CONNECT_TIME'], '%Y-%m-%d %H:%M:%S'),
                        ani_number=ani_number,
                        ingress_duration=ingress_duration,
                        dialed_number=dialed_number,
                        fecha=self.fecha,
                        compania_cdr=self.compania,
                        estado=activado,
                        motivo=observacion,
                        compania_ani=compania_ani_number,
                        tipo=tipo,
                        hora=dt.datetime.strptime(
                            row['CONNECT_TIME'], '%Y-%m-%d %H:%M:%S').time(),
                        date=dt.datetime.strptime(
                            row['CONNECT_TIME'], '%Y-%m-%d %H:%M:%S').date()
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
            valor_normal = valores.aggregate(Sum('valor'))
            valores_normales.append(valor_normal)
            duracion_normal = valores.aggregate(Sum('duracion'))

            valores = self.detfactura_set.filter(
                horario__startswith='reducido',
                fecha__range=(fecha_inicio, fecha_fin))
            valor_reducido = valores.aggregate(Sum('valor'))
            valores_reducidos.append(valor_reducido)
            duracion_reducido = valores.aggregate(Sum('duracion'))

            valores = self.detfactura_set.filter(
                horario__startswith='nocturno',
                fecha__range=(fecha_inicio, fecha_fin))
            valor_nocturno = valores.aggregate(Sum('valor'))
            valores_nocturnos.append(valor_nocturno)
            duracion_nocturno = valores.aggregate(Sum('duracion'))

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

        valor_total = self.detfactura_set.aggregate(Sum('valor'))
        total_segundos = self.detfactura_set.aggregate(Sum('duracion'))
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
        ordering = ('fecha',)

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
