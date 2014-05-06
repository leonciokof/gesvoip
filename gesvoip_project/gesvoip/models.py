import datetime as dt

from django.db import models


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

    def save(self, *args, **kwargs):
        if self.id is None:
            self.fecha = '{0}-{1}'.format(self.year, self. month)

        super(Cdr, self).save(*args, **kwargs)


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
    id_factura = models.IntegerField(primary_key=True)
    compania = models.ForeignKey(Compania, db_column='compania')
    fecha_inicio = models.TextField(blank=True)  # This field type is a guess.
    fecha_fin = models.TextField(blank=True)  # This field type is a guess.
    tarifa = models.TextField(blank=True)  # This field type is a guess.
    valor_normal = models.TextField(blank=True)  # This field type is a guess.
    valor_reducido = models.TextField(
        blank=True)  # This field type is a guess.
    valor_nocturno = models.TextField(
        blank=True)  # This field type is a guess.
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
