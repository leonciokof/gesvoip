from django.db import models
import django.db.models.options as options


options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)


class Ccaa(models.Model):
    id_ccaa = models.IntegerField()
    periodo = models.CharField(max_length=100, blank=True)
    concecionaria = models.CharField(max_length=100, blank=True)
    n_factura = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.CharField(max_length=100, blank=True)
    fecha_fin = models.CharField(max_length=100, blank=True)
    fecha_fact = models.CharField(max_length=100, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    trafico = models.IntegerField(blank=True, null=True)
    monto = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ccaa'
        in_db = 'sti'


class Cdr(models.Model):
    id_log = models.IntegerField()
    ani_number = models.IntegerField(blank=True, null=True)
    ingress_duration = models.IntegerField(blank=True, null=True)
    final_number = models.CharField(max_length=100, blank=True)
    fecha_cdr = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    idd = models.IntegerField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'cdr'
        in_db = 'sti'


class CentrosLocales(models.Model):
    cod_empresa = models.CharField(max_length=3, blank=True)
    cod_centro_local = models.CharField(primary_key=True, max_length=20)
    desp_centro_local = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'centros_locales'
        in_db = 'sti'


class Companias(models.Model):
    iddido = models.IntegerField(blank=True, null=True)
    cod_empresa = models.CharField(max_length=10, blank=True)
    nombre = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'companias'
        in_db = 'sti'


class Lineas(models.Model):
    numero = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=250, blank=True)
    tipo_persona = models.CharField(max_length=250, blank=True)
    comentarios = models.CharField(max_length=9999, blank=True)
    area = models.CharField(max_length=10, blank=True)
    comuna = models.CharField(max_length=10, blank=True)

    class Meta:
        db_table = 'lineas'
        in_db = 'sti'
