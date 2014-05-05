from django.db import models


class Cdr(models.Model):
    id = models.IntegerField(primary_key=True)
    fecha = models.CharField(max_length=255)
    compania = models.CharField(max_length=255)

    class Meta:
        db_table = 'cdr'


class Compania(models.Model):
    id_compania = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=255)
    entidad = models.CharField(max_length=255, blank=True)
    id = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True)
    codigo = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        db_table = 'compania'


class DetFactura(models.Model):
    id_detalle = models.IntegerField(primary_key=True)
    origen = models.DecimalField(max_digits=65535, decimal_places=65535)
    destino = models.DecimalField(max_digits=65535, decimal_places=65535)
    fecha = models.DateField()
    hora = models.CharField(max_length=255)
    duracion = models.DecimalField(max_digits=65535, decimal_places=65535)
    tarifa = models.ForeignKey('Tarifa', db_column='tarifa')
    horario = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=65535, decimal_places=65535)
    compania = models.ForeignKey(Compania, db_column='compania')
    factura = models.ForeignKey('Factura', db_column='factura')

    class Meta:
        db_table = 'det_factura'


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


class Feriado(models.Model):
    id_feriado = models.IntegerField(primary_key=True)
    fecha = models.DateField()

    class Meta:
        db_table = 'feriado'


class Horario(models.Model):
    id = models.IntegerField(primary_key=True)
    dia = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)
    inicio = models.TimeField(blank=True, null=True)
    fin = models.TimeField(blank=True, null=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'horario'


class Ido(models.Model):
    id = models.IntegerField(primary_key=True)
    codigo = models.IntegerField(unique=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'ido'


class LogLlamadas(models.Model):
    id_log = models.IntegerField(primary_key=True)
    connect_time = models.DateTimeField(blank=True, null=True)
    ani_number = models.CharField(max_length=255, blank=True)
    ingress_duration = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True)
    dialed_number = models.CharField(max_length=255, blank=True)
    fecha = models.CharField(max_length=7, blank=True)
    compania_cdr = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=255, blank=True)
    motivo = models.CharField(max_length=255, blank=True)
    compania_ani = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=100, blank=True)
    hora = models.TimeField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'log_llamadas'


class Numeracion(models.Model):
    id = models.IntegerField(primary_key=True)
    zona = models.IntegerField()
    rango = models.IntegerField()
    tipo = models.CharField(max_length=255, blank=True)
    compania = models.ForeignKey(Compania, db_column='compania')

    class Meta:
        db_table = 'numeracion'


class NumeracionAmpliada(models.Model):
    id_numeracion = models.IntegerField(primary_key=True)
    codigo = models.DecimalField(max_digits=65535, decimal_places=65535)
    numeracion = models.CharField(max_length=255)
    compania = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        db_table = 'numeracion_ampliada'


class Portados(models.Model):
    id = models.IntegerField(primary_key=True)
    numero = models.DecimalField(
        unique=True, max_digits=65535, decimal_places=65535)
    ido = models.IntegerField()
    tipo = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'portados'


class Tarifa(models.Model):
    id_tarifa = models.IntegerField(primary_key=True)
    compania = models.ForeignKey(Compania, db_column='compania')
    fecha = models.DateField()
    valor_normal = models.DecimalField(max_digits=65535, decimal_places=65535)
    valor_reducido = models.DecimalField(
        max_digits=65535, decimal_places=65535)
    valor_nocturno = models.DecimalField(
        max_digits=65535, decimal_places=65535)
    tipo = models.CharField(max_length=255, blank=True)
    id_ingreso = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True)

    class Meta:
        db_table = 'tarifa'


class Usuarios(models.Model):
    id_usuario = models.DecimalField(
        primary_key=True, max_digits=65535, decimal_places=65535)
    usuario = models.TextField()
    password = models.TextField(blank=True)
    nombre = models.TextField()
    apellido = models.TextField()
    correo = models.TextField(blank=True)
    rol = models.TextField()

    class Meta:
        db_table = 'usuarios'
