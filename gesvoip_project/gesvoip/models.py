# -*- coding: utf-8 -*-

import csv
try:
    import StringIO
except:
    from io import StringIO
import datetime as dt
import re

from django.conf import settings
from mongoengine.queryset import Q

from nptime import nptime
from pymongo import MongoClient
import arrow
import mongoengine

from . import choices, patterns


class Company(mongoengine.Document):

    """Modelo de compañias."""

    name = mongoengine.StringField(
        unique=True, max_length=255, verbose_name=u'nombre')
    idoidd = mongoengine.ListField(
        mongoengine.IntField(), verbose_name=u'idoidd')
    code = mongoengine.IntField(verbose_name=u'codigo')
    schedules = mongoengine.DictField(verbose_name=u'horarios')
    invoicing = mongoengine.StringField(
        choices=choices.INVOICING, verbose_name=u'facturación')
    id_compania = mongoengine.IntField()

    meta = {
        'ordering': ['name']
    }

    def __unicode__(self):
        return self.name


class Numeration(mongoengine.Document):

    """Modelo de las numeraciones."""

    numeration = mongoengine.StringField()
    company = mongoengine.ReferenceField(
        Company, reverse_delete_rule=mongoengine.CASCADE)

    meta = {
        'indexes': ['numeration']
    }

    def __unicode__(self):
        return self.numeration

    def get_range(self):
        return self._range

    @classmethod
    def upload(cls, filename):
        numbers = csv.DictReader(filename, delimiter=',')

        def reader_to_portability(reader):
            for r in reader:
                c = Company.objects.filter(
                    idoidd__in=[int(r['ido'])]).first()
                yield cls(
                    numeration='%s%s' % (r['zona'], r['rango']), company=c)

        cls.objects.delete()
        cls.objects.insert(reader_to_portability(numbers), load_bulk=False)


class Commune(mongoengine.Document):

    """Modelo que representa las comunas"""

    name = mongoengine.StringField(verbose_name='nombre')
    code = mongoengine.StringField(verbose_name='codigo')
    region = mongoengine.StringField(verbose_name='region')
    province = mongoengine.StringField(verbose_name='provincia')
    area = mongoengine.StringField(verbose_name='area')
    zone = mongoengine.StringField(verbose_name='zona')
    primary = mongoengine.StringField(verbose_name='primaria')

    def __unicode__(self):
        return self.name


class Line(mongoengine.Document):

    """Modelo de los clientes de convergia."""

    number = mongoengine.StringField(unique=True, verbose_name=u'numero')
    name = mongoengine.StringField(max_length=255, verbose_name=u'nombre')
    entity = mongoengine.StringField(
        choices=choices.ENTITIES, verbose_name=u'entidad')
    comments = mongoengine.StringField(verbose_name=u'comentarios')
    zone = mongoengine.IntField(verbose_name=u'area')
    city = mongoengine.IntField(verbose_name=u'comuna')
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
    commune = mongoengine.ReferenceField(Commune)

    meta = {
        'ordering': ['number'],
        'indexes': [('zone', 'city', 'entity', 'mode')]
    }

    def __unicode__(self):
        return str(self.number)

    @classmethod
    def get_services(cls, date):
        map_f = """
        function() {
            emit({commune: this.commune}, {count: 1, entity: this.entity});
        }"""
        reduce_f = """
        function(key, values) {
            var count = 0;
            values.forEach(function(v) {
                if (v.entity == 'empresa') {
                    count += v.count;
                }
            });
            return {count: count};
        }"""
        results = cls.objects.map_reduce(
            map_f, reduce_f, output='inline')

        def services_cb(obj):
            c = Commune.objects.get(pk=obj.key.get('commune'))
            return [
                314, date, c.primary, c.area, c.code, 1,
                'TB', 'RE', 'H', 'PP', 'D', '0', int(obj.value.get('count'))]

        r_filter = filter(lambda x: x.key.get('commune') is not None, results)

        return map(services_cb, r_filter)

    @classmethod
    def get_subscriptors(cls, date):
        count = cls.objects(
            entity='empresa', number__startswith='564469').count()

        return [[314, date, 'CO', count]] if count > 0 else [[]]


class Cdr(mongoengine.Document):

    """Modelo de los cdr."""

    year = mongoengine.StringField(
        max_length=4, choices=choices.YEARS, verbose_name='año', required=True)
    month = mongoengine.StringField(
        max_length=2, choices=choices.MONTHS, verbose_name='mes',
        required=True)
    incoming_ctc = mongoengine.FileField(verbose_name='CTC', required=True)
    incoming_entel = mongoengine.FileField(verbose_name='ENTEL', required=True)
    outgoing = mongoengine.FileField(verbose_name='STI', required=True)
    processed = mongoengine.BooleanField(default=False)

    def __unicode__(self):
        return u'{0}-{1}'.format(self.year, self.month)

    def get_date(self):
        """Retorna la fecha para traficos."""
        return self.year + self.month

    def get_day(self, connect_time, festives):
        if connect_time.date() in festives:
            return 'festive'

        else:
            if connect_time.weekday() in range(5):
                return 'bussines'

            elif connect_time.weekday() == 5:
                return 'saturday'

            else:
                return 'festive'

    def split_schedule(self, connect_time, duracion, compania):
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
            dia = compania.schedules.get(self.get_day(fecha_llamada))

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
            dia = compania.schedules.get(self.get_day(fecha_llamada))

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

    def get_timestamp(self, connect_time):
        return arrow.get(connect_time.format('H:mm:ss'), 'H:mm:ss').timestamp

    def insert_incoming(self):
        for c in choices.COMPANIAS:
            if c[0] == 'ENTEL':
                incoming = self.incoming_entel.read()

            else:
                incoming = self.incoming_ctc.read()

            incoming_file = StringIO.StringIO(incoming)
            incoming_dict = csv.DictReader(incoming_file, delimiter=',')

            def get_valid(ani, final_number, dialed_number, ingress_duration):
                p2 = re.search(patterns.national, final_number)
                p3 = re.search(patterns.special2, final_number)
                p4 = re.search(patterns.pattern_112, dialed_number)
                p5 = len(ani) == 11 and re.search(patterns.valid_ani, ani)
                p6 = int(ingress_duration) > 0

                return True if p2 and p3 and p4 and p5 and p6 else False

            def reader_to_incomming(reader):
                for r in reader:
                    connect_time = arrow.get(
                        r['CONNECT_TIME'], 'YYYY-MM-DD HH:mm:ss')
                    disconnect_time = arrow.get(
                        r['DISCONNECT_TIME'], 'YYYY-MM-DD HH:mm:ss')
                    valid = get_valid(
                        r['ANI'], r['FINAL_NUMBER'], r['DIALED_NUMBER'],
                        r['INGRESS_DURATION'])
                    obs = None if valid else 'No cumple con los filtros'
                    weekday = connect_time.weekday()

                    if weekday in range(5):
                        day = 'bussines'

                    elif weekday == 5:
                        day = 'saturday'

                    else:
                        day = 'festive'

                    yield Incoming(
                        connect_time=connect_time.datetime,
                        disconnect_time=disconnect_time.datetime,
                        ani=r['ANI'],
                        ani_number=r['ANI_NUMBER'],
                        ingress_duration=int(r['INGRESS_DURATION']),
                        dialed_number=r['DIALED_NUMBER'],
                        final_number=r['FINAL_NUMBER'],
                        cdr=self,
                        numeration=r['ANI'][2:][:6],
                        numeration5=r['ANI'][2:][:5],
                        weekday=weekday,
                        day=day,
                        timestamp=self.get_timestamp(connect_time),
                        date=connect_time.format('YYYY-MM-DD'),
                        valid=valid,
                        observation=obs)

            Incoming.objects.insert(
                reader_to_incomming(incoming_dict), load_bulk=False)

    def process_incoming(self):
        Incoming.set_festive(self)
        Incoming.set_type(self)
        Incoming.set_company(self)
        Incoming.set_schedule(self)

    def insert_outgoing(self):
        outgoing = self.outgoing.read()
        outgoing_file = StringIO.StringIO(outgoing)
        outgoing_dict = csv.DictReader(outgoing_file, delimiter=',')

        def reader_to_outgoing(reader):
            for r in reader:
                connect_time = arrow.get(
                    r['CONNECT_TIME'], 'YYYY-MM-DD HH:mm:ss')
                disconnect_time = arrow.get(
                    r['DISCONNECT_TIME'], 'YYYY-MM-DD HH:mm:ss')
                ingress_duration = int(r['INGRESS_DURATION'])

                if re.search(patterns.pattern_num_6, r['FINAL_NUMBER']):
                    numeration = r['FINAL_NUMBER'][2:][:6]

                else:
                    numeration = r['FINAL_NUMBER'][2:][:5]

                yield Outgoing(
                    connect_time=connect_time.datetime,
                    disconnect_time=disconnect_time.datetime,
                    ani=r['ANI'],
                    ani_number=r['ANI_NUMBER'],
                    final_number=r['FINAL_NUMBER'],
                    dialed_number=r['DIALED_NUMBER'],
                    ingress_duration=ingress_duration,
                    cdr=self,
                    numeration=numeration,
                    weekday=connect_time.weekday(),
                    timestamp=self.get_timestamp(connect_time))

        Outgoing.objects.insert(
            reader_to_outgoing(outgoing_dict), load_bulk=False)
        Outgoing.set_type(self)
        Outgoing.set_valid(self)
        Outgoing.set_company(self)
        Outgoing.set_schedule(self)
        Outgoing.set_entity(self)
        # Outgoing.set_line(self)

    def complete_invoices(self):
        for c in Company.objects(invoicing='monthly'):
            i = Invoice.objects(company=c, cdr=self).first()

            if i is not None:
                for p in Period.objects(invoice=i):
                    for r in Rate.objects(period=p):
                        end = arrow.get(p.end.date()).replace(days=1)
                        r.call_number = Incoming.objects(
                            company=c,
                            connect_time__gte=p.start.date(),
                            connect_time__lt=end.date(),
                            schedule=r._type).count()
                        r.call_duration = Incoming.objects(
                            company=c,
                            connect_time__gte=p.start.date(),
                            connect_time__lt=end.date(),
                            schedule=r._type).sum('ingress_duration')
                        r.total = r.call_duration * r.price
                        r.save()

                    p.call_number = Rate.objects(period=p).sum('call_number')
                    p.call_duration = Rate.objects(period=p).sum(
                        'call_duration')
                    p.total = Rate.objects(period=p).sum('total')
                    p.save()

                i.call_number = Period.objects(invoice=i).sum('call_number')
                i.call_duration = Period.objects(invoice=i).sum(
                    'call_duration')
                i.total = Period.objects(invoice=i).sum('total')
                i.invoiced = True
                i.save()

    def get_ingress_duration_by_type(self, company, _type, schedule):
        return Incoming.objects(
            cdr=self, company=company, _type=_type,
            schedule=schedule).sum('ingress_duration')

    def get_count_by_type(self, company, _type, schedule):
        return Incoming.objects(
            cdr=self, company=company, _type=_type,
            schedule=schedule).count()

    def get_outgoing_ingress_duration(self, company, _type, schedule):
        return Outgoing.objects(
            cdr=self, company=company, _type=_type, schedule=schedule,
            entity='empresa').sum('ingress_duration')

    def get_outgoing_count(self, company, _type, schedule):
        return Outgoing.objects(
            cdr=self, company=company, _type=_type, schedule=schedule,
            entity='empresa').count()

    def get_traffic(self, _type):
        items = []
        date = self.get_date()

        for c in Company.objects(invoicing='monthly'):
            for s in map(lambda x: x[0], choices.TIPO_CHOICES):
                ingress_duration = self.get_ingress_duration_by_type(
                    c, _type, s)
                count = self.get_count_by_type(c, _type, s)

                if ingress_duration > 0 and count > 0:
                    if _type == 'local':
                        items.append([
                            314, date, 'E', '06', '2', c.code, 'TB', 'CO',
                            'NOR', '0%s' % s, count, round(ingress_duration)])

                    elif _type == 'voip-local':
                        items.append([
                            314, date, 'E', c.code, 'CO', 'NOR',
                            '0%s' % s, count, round(ingress_duration),
                            round(ingress_duration) * 20])

                    elif _type == 'movil':
                        items.append([
                            314, date, 'E', c.code, '06', '2', 'TB', 'CO',
                            'NOR', '0%s' % s, count, round(ingress_duration)])

                    elif _type == 'voip-movil':
                        items.append([
                            314, date, 'E', c.code, 'CO', 'NOR',
                            '0%s' % s, count, round(ingress_duration),
                            round(ingress_duration) * 20])

                ingress_duration = self.get_outgoing_ingress_duration(
                    c, _type, s)
                count = self.get_outgoing_count(c, _type, s)

                if ingress_duration > 0 and count > 0:
                    if _type == 'local':
                        items.append([
                            314, date, 'S', '06', '2', c.code, 'TB', 'CO',
                            'NOR', '0%s' % s, count, round(ingress_duration)])

                    elif _type == 'voip-local':
                        items.append([
                            314, date, 'S', c.code, 'CO', 'NOR',
                            '0%s' % s, count, round(ingress_duration),
                            round(ingress_duration) * 20])

                    elif _type == 'movil':
                        items.append([
                            314, date, 'S', c.code, '06', '2', 'TB', 'CO',
                            'NOR', '0%s' % s, count, round(ingress_duration)])

                    elif _type == 'voip-movil':
                        items.append([
                            314, date, 'S', c.code, 'CO', 'NOR',
                            '0%s' % s, count, round(ingress_duration),
                            round(ingress_duration) * 20])

                    elif _type == 'internacional':
                        items.append([
                            314, date, 'LDI', 'S', 112, '06', 2, 'TB', 'CO',
                            'NOR', '0%s' % s, count, round(ingress_duration)])

        return items


class Incoming(mongoengine.Document):

    """Modelo de las llamdas entrantes."""

    connect_time = mongoengine.DateTimeField()
    disconnect_time = mongoengine.DateTimeField()
    ani = mongoengine.StringField()
    final_number = mongoengine.StringField()
    ani_number = mongoengine.StringField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.StringField()
    cdr = mongoengine.ReferenceField(
        Cdr, reverse_delete_rule=mongoengine.CASCADE)
    valid = mongoengine.BooleanField(default=False)
    invoiced = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)
    _type = mongoengine.StringField()
    schedule = mongoengine.StringField()
    entity = mongoengine.StringField()
    numeration = mongoengine.StringField()
    numeration5 = mongoengine.StringField()
    day = mongoengine.StringField()
    weekday = mongoengine.IntField()
    timestamp = mongoengine.IntField()
    date = mongoengine.StringField()

    def __unicode__(self):
        return str(self.connect_time)

    @property
    def type(self):
        return self._type

    @classmethod
    def set_festive(cls, cdr):
        date = '%s-%s' % (cdr.year, cdr.month)
        start = arrow.get('%s-01' % date, 'YYYY-MM-DD')
        end = start.replace(months=1)
        festives = Holiday.objects(
            date__gte=start, date__lt=end).values_list('date')
        festives = [f.format('YYYY-MM-DD') for f in festives]
        cls.objects(
            cdr=cdr, valid=True, date__in=festives).update(set__day='festive')

    @classmethod
    def set_type(cls, cdr):
        """Funcion que establece el tipo de llamada"""
        cls.objects(
            cdr=cdr, final_number=patterns.voip,
            ani=patterns.movil).update(set___type='voip-movil')
        cls.objects(
            cdr=cdr, final_number=patterns.voip,
            ani=patterns.international,
            _type=None).update(set___type='voip-ldi')
        cls.objects(
            cdr=cdr, final_number=patterns.voip,
            _type=None).update(set___type='voip-local')
        cls.objects(
            cdr=cdr, final_number=patterns.normal,
            ani=patterns.movil, _type=None).update(set___type='movil')
        cls.objects(
            cdr=cdr, final_number=patterns.normal,
            ani=patterns.international,
            _type=None).update(set___type='internacional')
        cls.objects(
            cdr=cdr, final_number=patterns.normal,
            ani=patterns.santiago, _type=None).update(set___type='local')
        cls.objects(
            cdr=cdr, final_number=patterns.normal,
            ani=patterns.special, _type=None).update(set___type='especial')
        cls.objects(
            cdr=cdr, final_number=patterns.normal,
            _type=None).update(set___type='nacional')

    @classmethod
    def set_company(cls, cdr):
        date = '%s-%s' % (cdr.year, cdr.month)
        start = arrow.get('%s-01' % date, 'YYYY-MM-DD')
        end = start.replace(months=1)

        for c in Portability.objects.distinct('company'):
            numbers = list(Portability.objects(
                company=c, date__lt=end.datetime).values_list('number'))
            cls.objects(
                cdr=cdr, valid=True, ani__in=numbers).update(set__company=c)

        for c in Numeration.objects.distinct('company'):
            numerations = list(Numeration.objects(company=c).values_list(
                'numeration'))
            cls.objects(
                cdr=cdr, valid=True, numeration__in=numerations,
                company=None).update(set__company=c)
            cls.objects(
                cdr=cdr, valid=True, numeration5__in=numerations,
                company=None).update(set__company=c)

        cls.objects(
            cdr=cdr, valid=True, company=None).update(
                set__valid=False, set__observation='Sin empresa')

    @classmethod
    def set_schedule(cls, cdr):
        cls.objects(
            cdr=cdr, valid=True, day='bussines',
            timestamp__gte=arrow.get('9:00:00', 'H:mm:ss').timestamp,
            timestamp__lte=arrow.get('22:59:59', 'H:mm:ss').timestamp).update(
                set__schedule='normal')
        cls.objects(
            cdr=cdr, valid=True, day__in=['saturday', 'festive'],
            timestamp__gte=arrow.get('9:00:00', 'H:mm:ss').timestamp,
            timestamp__lte=arrow.get('22:59:59', 'H:mm:ss').timestamp).update(
                set__schedule='reducido')
        cls.objects(cdr=cdr, valid=True, schedule=None).update(
            set__schedule='nocturno')


class Outgoing(mongoengine.Document):

    """Modelo de las llamdas salientes."""

    connect_time = mongoengine.DateTimeField()
    disconnect_time = mongoengine.DateTimeField()
    ani = mongoengine.StringField()
    final_number = mongoengine.StringField()
    ani_number = mongoengine.StringField()
    ingress_duration = mongoengine.IntField()
    dialed_number = mongoengine.StringField()
    cdr = mongoengine.ReferenceField(
        Cdr, reverse_delete_rule=mongoengine.CASCADE)
    valid = mongoengine.BooleanField(default=False)
    observation = mongoengine.StringField(default='No cumple con los filtros')
    company = mongoengine.ReferenceField(Company)
    line = mongoengine.ReferenceField(Line)
    _type = mongoengine.StringField()
    schedule = mongoengine.StringField()
    entity = mongoengine.StringField()
    numeration = mongoengine.StringField()
    weekday = mongoengine.IntField()
    timestamp = mongoengine.IntField()

    def __unicode__(self):
        return str(self.connect_time)

    @classmethod
    def set_type(cls, cdr):
        cls.objects(
            cdr=cdr, ani=patterns.pattern_56446,
            final_number=patterns.movil).update(set___type='voip-movil')
        cls.objects(
            cdr=cdr, ani=patterns.pattern_56446,
            final_number=patterns.national,
            _type=None).update(set___type='voip-local')
        cls.objects(
            cdr=cdr, ani=patterns.national,
            final_number=patterns.movil, _type=None).update(set___type='movil')
        q = {
            'cdr': cdr.id,
            'ani': patterns.national,
            '_type': None,
            'final_number': patterns.national,
            'final_number': patterns.pattern_not_56446}
        cls.objects(__raw__=q).update(set___type='local')
        cls.objects(
            cdr=cdr, ani=patterns.national,
            final_number=patterns.international,
            _type=None).update(set___type='internacional')

    @classmethod
    def set_valid(cls, cdr):
        cls.objects(cdr=cdr, _type__ne=None, ingress_duration__gt=0).update(
            set__valid=True, set__observation=None)

    @classmethod
    def set_company(cls, cdr):
        date = '%s-%s' % (cdr.year, cdr.month)
        start = arrow.get('%s-01' % date, 'YYYY-MM-DD')
        end = start.replace(months=1)

        for c in Portability.objects.distinct('company'):
            numbers = list(Portability.objects(
                company=c, date__lt=end.datetime).values_list('number'))
            cls.objects(
                cdr=cdr, valid=True,
                final_number__in=numbers).update(set__company=c)

        for c in Numeration.objects.distinct('company'):
            numerations = list(Numeration.objects(company=c).values_list(
                'numeration'))
            cls.objects(
                cdr=cdr, valid=True, numeration__in=numerations,
                company=None).update(set__company=c)

        cls.objects(
            cdr=cdr, valid=True, company=None).update(
                set__valid=False, set__observation='Sin empresa')

    @classmethod
    def set_schedule(cls, cdr):
        def start(hour):
            return arrow.get(1, 1, 1, hour).timestamp

        def end(hour):
            return arrow.get(1, 1, 1, hour, 59, 59).timestamp

        q1 = Q(cdr=cdr) & Q(valid=True)
        q2 = Q(weekday__gte=0) & Q(weekday__lte=4)
        q3 = Q(timestamp__gte=start(8)) & Q(timestamp__lte=end(19))
        q4 = Q(weekday=5)
        q5 = Q(timestamp__gte=start(8)) & Q(timestamp__lte=end(13))
        cls.objects(q1 & ((q2 & q3) | (q4 & q5))).update(
            set__schedule='normal')
        q1 = Q(cdr=cdr) & Q(valid=True) & Q(schedule=None)
        q3 = Q(timestamp__gte=start(20)) & Q(timestamp__lte=end(23))
        q5 = Q(timestamp__gte=start(14)) & Q(timestamp__lte=end(23))
        q6 = Q(weekday=6)
        q7 = Q(timestamp__gte=start(8)) & Q(timestamp__lte=end(23))
        cls.objects(q1 & ((q2 & q3) | (q4 & q5) | (q6 & q7))).update(
            set__schedule='reducido')
        cls.objects(
            cdr=cdr, valid=True, schedule=None, timestamp__gte=start(0),
            timestamp__lte=end(7)).update(set__schedule='nocturno')

    @classmethod
    def set_entity(cls, cdr):
        for e in Line.objects.distinct('entity'):
            numbers = list(Line.objects(entity=e).values_list(
                'number'))
            Outgoing.objects(
                cdr=cdr, valid=True, final_number__in=numbers).update(
                    set__entity=e)

    @classmethod
    def set_line(cls, cdr):
        for l in Line.objects.all():
            Outgoing.objects(
                cdr=cdr, valid=True, ani_number=l.number).update(set__line=l)


class Portability(mongoengine.Document):

    """Modelo de los numeros portados."""

    number = mongoengine.StringField()
    company = mongoengine.ReferenceField(Company)
    _type = mongoengine.IntField()
    date = mongoengine.DateTimeField()
    ido = mongoengine.IntField()

    def __unicode__(self):
        return str(self.number)

    @classmethod
    def upload(cls, filename):
        numbers = csv.DictReader(filename, delimiter=',')

        def reader_to_portability(reader):
            for r in reader:
                yield {
                    'date': dt.datetime.strptime(
                        r['fecha'], '%Y%m%d'),
                    'number': r['numero'],
                    'ido': int(r['ido']),
                    '_type': int(r['tipo'])}

        db = MongoClient(settings.MONGODB_URI).gesvoip
        db.portability.remove()
        db.portability.insert(reader_to_portability(numbers))

        for c in Company.objects.all():
            cls.objects.filter(ido__in=c.idoidd).update(set__company=c)


class Holiday(mongoengine.Document):

    """Modelo de los feriados."""

    date = mongoengine.DateTimeField(unique=True, verbose_name=u'fecha')
    reason = mongoengine.StringField(max_length=255, choices=choices.HOLIDAYS)

    meta = {
        'ordering': ['-date']
    }

    def __unicode__(self):
        return str(self.date)


class Invoice(mongoengine.Document):

    """Modelo de facturas."""

    company = mongoengine.ReferenceField(Company)
    cdr = mongoengine.ReferenceField(
        Cdr, reverse_delete_rule=mongoengine.CASCADE)
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()
    invoiced = mongoengine.BooleanField(default=False)
    code = mongoengine.SequenceField()

    def __unicode__(self):
        return self.get_date()

    def get_date(self):
        return u'{0}-{1}'.format(self.cdr.year, self.cdr.month)

    def get_total(self):
        return int(round(self.total)) if self.total else 0

    def get_periods(self):
        return Period.objects(invoice=self)


class Period(mongoengine.Document):

    """Modelo que representa los periodos de las facturas"""

    invoice = mongoengine.ReferenceField(Invoice)
    start = mongoengine.DateTimeField()
    end = mongoengine.DateTimeField()
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()

    def __unicode__(self):
        return self.get_range()

    def get_start(self):
        return self.start.strftime('%Y-%m-%d')

    def get_end(self):
        return self.end.strftime('%Y-%m-%d')

    def get_range(self):
        return u'{0} - {1}'.format(self.get_start(), self.get_end())

    def get_rates(self):
        return Rate.objects(period=self)

    def get_total(self):
        return int(round(self.total)) if self.total else 0


class Rate(mongoengine.Document):

    """Modelo que representa las tarifas de las compañias"""

    period = mongoengine.ReferenceField(Period)
    _type = mongoengine.StringField()
    price = mongoengine.FloatField()
    call_number = mongoengine.IntField()
    call_duration = mongoengine.IntField()
    total = mongoengine.FloatField()

    def __unicode__(self):
        return self._type

    def get_type(self):
        return self._type

    def get_total(self):
        return int(round(self.total)) if self.total else 0


class LocalCenter(mongoengine.Document):

    """Modelo que representa los centros locales"""

    company = mongoengine.ReferenceField(Company)
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
    schedule = mongoengine.StringField(verbose_name=u'tipo horario')
    call_duration = mongoengine.IntField(verbose_name=u'trafico')
    total = mongoengine.IntField(verbose_name=u'monto')

    def __unicode__(self):
        return u'{0} {1}'.format(self.get_date(), self.company)

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

        def report_cb(obj):
            return [
                314,
                date,
                obj.company.code,
                obj.invoice,
                obj.start.strftime('%Y%m%d'),
                obj.end.strftime('%Y%m%d'),
                'PCA',
                obj.invoice_date.strftime('%Y%m%d'),
                obj.get_schedule(),
                '',
                obj.call_duration,
                obj.total]

        return map(report_cb, cls.objects(year=year, month=month))
