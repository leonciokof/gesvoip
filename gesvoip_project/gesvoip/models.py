# -*- coding: utf-8 -*-

import datetime as dt
import re

from nptime import nptime
import mongoengine

from . import choices, patterns


class Company(mongoengine.Document):

    """Modelo de compañias."""

    name = mongoengine.StringField(
        unique=True, max_length=255, verbose_name=u'nombre')
    code = mongoengine.IntField(verbose_name=u'codigo')
    schedules = mongoengine.DictField(verbose_name=u'horarios')
    invoicing = mongoengine.StringField(
        choices=choices.INVOICING, verbose_name=u'facturación')

    meta = {
        'ordering': ['name']
    }

    def __unicode__(self):
        return self.name


class Numeration(mongoengine.Document):

    """Modelo de las numeraciones."""

    zone = mongoengine.IntField()
    _range = mongoengine.IntField()
    company = mongoengine.ReferenceField(Company)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())

    def get_range(self):
        return self._range


class Line(mongoengine.Document):

    """Modelo de los clientes de convergia."""

    number = mongoengine.IntField(unique=True, verbose_name=u'numero')
    name = mongoengine.StringField(max_length=255, verbose_name=u'nombre')
    entity = mongoengine.StringField(
        choices=choices.ENTITIES, verbose_name=u'entidad')
    comments = mongoengine.StringField(verbose_name=u'comentarios')
    zone = mongoengine.IntField(choices=choices.ZONES, verbose_name=u'area')
    city = mongoengine.IntField(choices=choices.CITIES, verbose_name=u'comuna')
    company = mongoengine.IntField(default=333)
    rut = mongoengine.StringField(
        max_length=12, verbose_name=u'rut propietario')
    service = mongoengine.StringField(
        choices=choices.SERVICES, verbose_name=u'servicio', default='voip')
    mode = mongoengine.StringField(
        choices=choices.MODES, verbose_name=u'modalidad', default='postpago')
    due = mongoengine.FloatField(verbose_name=u'deuda vencida', default=0.0000)
    active = mongoengine.BooleanField(default=False, verbose_name=u'activo')
    document = mongoengine.IntField(verbose_name=u'documento')
    special_service = mongoengine.StringField(
        choices=choices.SPECIAL_SERVICES, verbose_name=u'servicio especial')

    meta = {
        'ordering': ['number'],
        'indexes': [('zone', 'city', 'entity', 'mode')]
    }

    def __unicode__(self):
        return unicode(self.number)

    @classmethod
    def get_services(cls, date):
        items = []
        primary = ''

        for zone, name1 in choices.ZONES:
            for city, name2 in choices.CITIES:
                if zone == 58:
                    primary = '01'
                elif zone == 57:
                    primary = '02'
                elif zone == 55:
                    primary = '03'
                elif zone in (51, 52, 53):
                    primary = '04'
                elif zone in (32, 33, 34, 35):
                    primary = '05'
                elif zone == 2:
                    primary = '06'
                elif zone == 72:
                    primary = '07'
                elif zone in (75, 73, 71):
                    primary = '08'
                elif zone in (41, 42, 43):
                    primary = '09'
                elif zone == 45:
                    primary = 10
                elif zone in (63, 65, 64):
                    primary = 11
                elif zone == 67:
                    primary = 12
                elif zone == 61:
                    primary = 13

                post_natural = cls.objects.filter(
                    zone=zone, city=city, entity='natural',
                    mode='postpago').count()
                pre_natural = cls.objects.filter(
                    zone=zone, city=city, entity='natural',
                    mode='prepago').count()
                post_empresa = cls.objects.filter(
                    zone=zone, city=city, entity='empresa',
                    mode='postpago').count()

                if post_natural > 0:
                    items.append([
                        314, date, primary, zone, city, 1,
                        'TB', 'RE', 'H', 'PA', 'D', '0', post_natural])
                if pre_natural > 0:
                    items.append([
                        314, date, primary, zone, city, 1,
                        'TB', 'CO', 'H', 'PA', 'D', '0', pre_natural])
                if post_empresa > 0:
                    items.append([
                        314, date, primary, zone, city, 1,
                        'TB', 'RE', 'H', 'PP', 'D', '0', post_empresa])

        return items

    @classmethod
    def get_subscriptors(cls, date):
        items = []
        natural = cls.objects.filter(
            entity='natural', number__gte=56446900000,
            number__lte=56446999999).count()
        empresa = cls.objects.filter(
            entity='empresa', number__gte=56446900000,
            number__lte=56446999999).count()

        if natural > 0:
            items.append([314, date, 'RE', natural])
        if empresa > 0:
            items.append([314, date, 'CO', empresa])

        return items


class Cdr(mongoengine.Document):

    """Modelo de los cdr."""

    month = mongoengine.StringField(
        max_length=2, choices=choices.MONTHS)
    year = mongoengine.StringField(
        max_length=4, choices=choices.YEARS)
    incoming_ctc = mongoengine.FileField()
    incoming_entel = mongoengine.FileField()
    outgoing = mongoengine.FileField()
    processed = mongoengine.BooleanField(default=False)

    def __unicode__(self):
        return u'{0}-{1}'.format(self.year, self.month)

    def valida_ani(self, ani):
        if len(ani) == 11:
            return True

        else:
            return False

    def get_activado_ctc(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if re.search(patterns.pattern_569, ani):
            return True

        elif (re.search(patterns.pattern_562, ani)
                and not re.search(patterns.pattern_800, dialed_number)):
            return True

        elif re.search(patterns.pattern_4469v2, dialed_number):
            return True

        else:
            return False

    def get_activado_entel(self, ani, dialed_number):
        """Funcion que determina si un registro debe o no ser facturado"""
        if re.search(patterns.pattern_0234469v2, dialed_number):
            return True

        elif (re.search(patterns.pattern_64469, dialed_number) and
                not re.search(patterns.pattern_112, dialed_number)):
            return True

        else:
            return False

    def get_zona_rango(self, ani):
        """Retorna la zona y rango del ani_number"""
        if re.search(patterns.pattern_569, ani):
            return ani[2:][:1], ani[3:][:4]

        elif re.search(patterns.pattern_9, ani):
            return ani[2:][:2], ani[4:][:4]

        elif re.search(patterns.pattern_562, ani):
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
        if re.search(patterns.pattern_564469, final_number):
            if re.search(patterns.pattern_569, ani):
                return 'voip-movil'

            elif not re.search(patterns.pattern_56, ani):
                return 'voip-ldi'

            else:
                return 'voip-local'

        else:
            if re.search(patterns.pattern_569, ani):
                return 'movil'

            elif not re.search(patterns.pattern_56, ani):
                return 'internacional'

            elif re.search(patterns.pattern_562, ani):
                return 'local'

            elif re.search(patterns.pattern_5610, ani):
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
        def get_horario(name):
            tipo = dia.get(name)

            if tipo:
                start = dt.datetime.strptime(tipo['start'], '%H:%M:%S').time()
                end = dt.datetime.strptime(tipo['end'], '%H:%M:%S').time()

                if start < end:
                    if start <= hora_llamada <= end:
                        return name

                else:
                    if start <= hora_llamada <= dt.time(23, 59, 59):
                        return name

                    elif dt.time(0, 0) <= hora_llamada <= end:
                        return name

            else:
                return None

        dia = compania.schedules.get(self.get_dia(fecha_llamada))

        if dia:
            for n in ['normal', 'reducido', 'nocturno']:
                tipo = get_horario(n)

                if tipo is not None:
                    return tipo

        else:
            return None

    def split_horario(self, connect_time, duracion, compania):
        def split1(start, end):
            start = nptime().from_time(
                dt.datetime.strptime(start, '%H:%M:%S').time())
            end = nptime().from_time(
                dt.datetime.strptime(end, '%H:%M:%S').time())

            if hora_inicio < start < hora_fin:
                duracion1 = int((start - hora_inicio).total_seconds())
                duracion2 = int((hora_fin - start).total_seconds())

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': duracion1
                    },
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': start,
                        'duracion': duracion2})

            elif hora_inicio < end < hora_fin:
                duracion1 = int((end - hora_inicio).total_seconds())
                duracion2 = int((hora_fin - end).total_seconds())

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': duracion1
                    },
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': end + dt.timedelta(seconds=1),
                        'duracion': duracion2})

            else:
                return None

        def split2(start, end):
            start = nptime().from_time(
                dt.datetime.strptime(start, '%H:%M:%S').time())
            end = nptime().from_time(
                dt.datetime.strptime(end, '%H:%M:%S').time())

            if hora_inicio < start < dt.time(23, 59, 59):
                duracion1 = int((start - hora_inicio).total_seconds())
                duracion2 = int((nptime(23, 59, 59) - start).total_seconds())
                duracion3 = int((hora_fin - nptime(0, 0)).total_seconds()) + 1

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': duracion1
                    },
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': start,
                        'duracion': duracion2
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': nptime(0, 0),
                        'duracion': duracion3})

            elif hora_inicio < end < dt.time(23, 59, 59):
                duracion1 = int((end - hora_inicio).total_seconds())
                duracion2 = int((nptime(23, 59, 59) - end).total_seconds())
                duracion3 = int((hora_fin - nptime(0, 0)).total_seconds()) + 1

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': duracion1
                    },
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': end + dt.timedelta(seconds=1),
                        'duracion': duracion2
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': nptime(0, 0),
                        'duracion': duracion3
                    }
                )

            elif dt.time(0, 0) < start < hora_fin:
                d1 = int((nptime(23, 59, 59) - hora_inicio).total_seconds())
                d2 = int((start - nptime(0, 0)).total_seconds()) + 1
                d3 = int((hora_fin - start).total_seconds())

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': d1
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': nptime(0, 0),
                        'duracion': d2
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': start,
                        'duracion': d3})

            elif dt.time(0, 0) <= end <= hora_fin:
                d1 = int((nptime(23, 59, 59) - hora_inicio).total_seconds())
                d2 = int((end - nptime(0, 0)).total_seconds()) + 1
                d3 = int((hora_fin - end).total_seconds())

                return (
                    {
                        'fecha_llamada': fecha_llamada,
                        'hora_inicio': hora_inicio,
                        'duracion': d1
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': nptime(0, 0),
                        'duracion': d2
                    },
                    {
                        'fecha_llamada': fecha_llamada + dt.timedelta(
                            days=1),
                        'hora_inicio': end + dt.timedelta(seconds=1),
                        'duracion': d3
                    },
                )

            else:
                return None

        fecha_llamada = connect_time.date()
        hora_inicio = nptime().from_time(connect_time.time())
        hora_fin = hora_inicio + dt.timedelta(seconds=float(duracion))

        if hora_inicio <= hora_fin:
            dia = compania.schedules.get(self.get_dia(fecha_llamada))

            if dia:
                for n in ['normal', 'reducido', 'nocturno']:
                    tipo = dia.get(n)

                    if tipo:
                        output = split1(tipo['start'], tipo['end'])

                        if output is not None:
                            return output

            return ({
                'fecha_llamada': fecha_llamada,
                'hora_inicio': hora_inicio,
                'duracion': duracion},)

        else:
            dia = compania.schedules.get(self.get_dia(fecha_llamada))

            if dia:
                for n in ['normal', 'reducido', 'nocturno']:
                    tipo = dia.get(n)

                    if tipo:
                        output = split2(tipo['start'], tipo['end'])

                        if output is not None:
                            return output

            return ({
                'fecha_llamada': fecha_llamada,
                'hora_inicio': hora_inicio,
                'duracion': duracion},)

    def get_entity(self, dialed_number):
        if len(dialed_number) == 8 and dialed_number[0] == '2':
            numero = int('562' + dialed_number)

        else:
            numero = int('56' + dialed_number)
        linea = Line.objects.filter(number=numero).first()

        return None if linea is None else linea.entity

    def insert_incoming(self, name):
        startTime = dt.datetime.now()
        if name == 'ENTEL':
            lines = [
                r.split(',')
                for r in self.incoming_entel.read().decode().split('\r\n')[:-1]
            ]
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
                    Incoming(
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
                    ).save()

            else:
                Incoming(
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
                ).save()

        print(dt.datetime.now() - startTime)

        return True


class Incoming(mongoengine.Document):

    """Modelo de las llamdas entrantes."""

    connect_time = mongoengine.DateTimeField()
    ani_number = mongoengine.IntField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.IntField()
    cdr = mongoengine.ReferenceField(Cdr)
    valid = mongoengine.BooleanField()
    invoiced = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)
    _type = mongoengine.StringField(choices=choices.TIPOS)
    schedule = mongoengine.StringField(choices=choices.TIPO_CHOICES)
    entity = mongoengine.StringField(choices=choices.ENTITIES)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())


class Outgoing(mongoengine.Document):

    """Modelo de las llamdas salientes."""

    connect_time = mongoengine.DateTimeField()
    ani_number = mongoengine.IntField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.IntField()
    cdr = mongoengine.ReferenceField(Cdr)
    valid = mongoengine.BooleanField()
    invoiced = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())


class Portability(mongoengine.Document):

    """Modelo de los numeros portados."""

    number = mongoengine.IntField(unique=True)
    company = mongoengine.ReferenceField(Company)
    date = mongoengine.DateTimeField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())


class Holiday(mongoengine.Document):

    """Modelo de los feriados."""

    date = mongoengine.DateTimeField(unique=True, verbose_name=u'fecha')

    meta = {
        'ordering': ['-date']
    }

    def __unicode__(self):
        return self.date.strftime('%Y-%m-%d')


class Invoice(mongoengine.Document):

    """Modelo de facturas."""

    company = mongoengine.ReferenceField(Company)
    month = mongoengine.StringField(
        max_length=2, choices=choices.MONTHS)
    year = mongoengine.StringField(
        max_length=4, choices=choices.YEARS)
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()
    invoiced = mongoengine.BooleanField(default=False)
    code = mongoengine.SequenceField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())

    def get_date(self):
        return u'{0}-{1}'.format(self.year, self.month)

    def get_total(self):
        return int(round(self.total)) if self.total else 0

    def get_periods(self):
        return Period.objects.filter(invoice=self)


class Period(mongoengine.Document):

    """Modelo que representa los periodos de las facturas"""

    invoice = mongoengine.ReferenceField(Invoice)
    start = mongoengine.DateTimeField()
    end = mongoengine.DateTimeField()
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())

    def get_start(self):
        return self.start.strftime('%Y-%m-%d')

    def get_end(self):
        return self.end.strftime('%Y-%m-%d')

    def get_range(self):
        return u'{0} - {1}'.format(self.get_start(), self.get_end())

    def get_rates(self):
        return Rate.objects.filter(period=self)

    def get_total(self):
        return int(round(self.total)) if self.total else 0


class Rate(mongoengine.Document):

    """Modelo que representa las tarifas de las compañias"""

    period = mongoengine.ReferenceField(Period)
    _type = mongoengine.StringField(choices=choices.TIPO_CHOICES)
    price = mongoengine.FloatField()
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.__str__())

    def get_type(self):
        return self.get__type_display()

    def get_total(self):
        return int(round(self.total)) if self.total else 0


class LocalCenter(mongoengine.Document):

    """Modelo que representa los centros locales"""

    company = mongoengine.IntField(default=314, verbose_name=u'codigo empresa')
    code = mongoengine.IntField(unique=True, verbose_name=u'codigo local')
    name = mongoengine.StringField(
        max_length=255, verbose_name=u'descripción local')

    def __unicode__(self):
        return self.name


class Ccaa(mongoengine.Document):

    """Modelo que representa los cargos de acceso"""

    month = mongoengine.StringField(
        max_length=2, choices=choices.MONTHS, verbose_name=u'mes')
    year = mongoengine.StringField(
        max_length=4, choices=choices.YEARS, verbose_name=u'año')
    company = mongoengine.ReferenceField(
        Company, verbose_name=u'concecionaria interconectada')
    invoice = mongoengine.IntField(verbose_name=u'número factura')
    start = mongoengine.DateTimeField(verbose_name=u'fecha inicio')
    end = mongoengine.DateTimeField(verbose_name=u'fecha fin')
    invoice_date = mongoengine.DateTimeField(
        verbose_name=u'fecha emision factura')
    schedule = mongoengine.StringField(
        choices=choices.TIPO_CHOICES, verbose_name=u'tipo horario')
    call_duration = mongoengine.IntField(verbose_name=u'trafico')
    total = mongoengine.IntField(verbose_name=u'monto')

    def __unicode__(self):
        return u'{0}-{1} {2}'.format(self.year, self.month, self.company)

    def get_date(self):
        return u'{0}-{1}'.format(self.year, self.month)

    def get_schedule(self):
        if self.schedule == 'normal':
            return 'N'

        elif self.schedule == 'reducido':
            return 'R'

        else:
            return 'O'

    @classmethod
    def get_report(cls, year, month):
        date = year + month
        items = []

        for c in cls.objects.filter(year=year, month=month):
            items.append([
                314, date, c.company.code, c.invoice,
                c.start.strftime('%Y%m%d'), c.end.strftime('%Y%m%d'), 'PCA',
                c.invoice_date.strftime('%Y%m%d'), c.get_schedule(), '',
                c.call_duration, c.total])

        return items
