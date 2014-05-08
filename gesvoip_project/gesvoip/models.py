# -*- coding: utf-8 -*-

from re import search
import datetime as dt

from django.db import models

from djorm_pgarray.fields import ArrayField

from . import patterns


class Cdr(models.Model):

    def update_filename(instance, filename):
        return 'logs/{0}-{1}-{2}.log'.format(
            instance.year, instance.month, instance.compania)

    COMPANIAS = (
        ('ENTEL', 'ENTEL'),
        ('CTC', 'CTC'),
    )
    MONTHS = (
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    )
    YEARS = [
        ('{0}'.format(i), '{0}'.format(i))
        for i in range(dt.date.today().year, 2000, -1)
    ]
    id = models.AutoField(primary_key=True)
    fecha = models.CharField(max_length=255, blank=True)
    compania = models.CharField(max_length=255, choices=COMPANIAS)
    month = models.CharField(
        max_length=2, choices=MONTHS, default='', blank=True)
    year = models.CharField(
        max_length=4, choices=YEARS, default='', blank=True)
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
            p.numero: Ido.objects.get(codigo=p.ido).compania.pk
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
                        compania_ani=compania_ani_number.id_compania,
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
    usuario = models.ForeignKey('Usuarios', db_column='usuario')

    class Meta:
        db_table = 'factura'
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'

    def __unicode__(self):
        return u'{0}'.format(self.id_factura)


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
