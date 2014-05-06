# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cdr'
        db.create_table('cdr', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('fecha', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('compania', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'gesvoip', ['Cdr'])

        # Adding model 'Compania'
        db.create_table('compania', (
            ('id_compania', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('rut', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('entidad', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('codigo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'gesvoip', ['Compania'])

        # Adding model 'DetFactura'
        db.create_table('det_factura', (
            ('id_detalle', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('origen', self.gf('django.db.models.fields.IntegerField')()),
            ('destino', self.gf('django.db.models.fields.IntegerField')()),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('hora', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('duracion', self.gf('django.db.models.fields.FloatField')()),
            ('tarifa', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Tarifa'], db_column='tarifa')),
            ('horario', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('valor', self.gf('django.db.models.fields.FloatField')()),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
            ('factura', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Factura'], db_column='factura')),
        ))
        db.send_create_signal(u'gesvoip', ['DetFactura'])

        # Adding model 'Factura'
        db.create_table('factura', (
            ('id_factura', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
            ('fecha_inicio', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('fecha_fin', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tarifa', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('valor_normal', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('valor_reducido', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('valor_nocturno', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('usuario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Usuarios'], db_column='usuario')),
        ))
        db.send_create_signal(u'gesvoip', ['Factura'])

        # Adding model 'Feriado'
        db.create_table('feriado', (
            ('id_feriado', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'gesvoip', ['Feriado'])

        # Adding model 'Horario'
        db.create_table('horario', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('dia', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('inicio', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('fin', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
        ))
        db.send_create_signal(u'gesvoip', ['Horario'])

        # Adding model 'Ido'
        db.create_table('ido', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('codigo', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
        ))
        db.send_create_signal(u'gesvoip', ['Ido'])

        # Adding model 'LogLlamadas'
        db.create_table('log_llamadas', (
            ('id_log', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('connect_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ani_number', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ingress_duration', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('dialed_number', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('fecha', self.gf('django.db.models.fields.CharField')(max_length=7, blank=True)),
            ('compania_cdr', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('estado', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('motivo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('compania_ani', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('hora', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'gesvoip', ['LogLlamadas'])

        # Adding model 'Numeracion'
        db.create_table('numeracion', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('zona', self.gf('django.db.models.fields.IntegerField')()),
            ('rango', self.gf('django.db.models.fields.IntegerField')()),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
        ))
        db.send_create_signal(u'gesvoip', ['Numeracion'])

        # Adding model 'NumeracionAmpliada'
        db.create_table('numeracion_ampliada', (
            ('id_numeracion', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('codigo', self.gf('django.db.models.fields.IntegerField')()),
            ('numeracion', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
        ))
        db.send_create_signal(u'gesvoip', ['NumeracionAmpliada'])

        # Adding model 'Portados'
        db.create_table('portados', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('numero', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('ido', self.gf('django.db.models.fields.IntegerField')()),
            ('tipo', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('fecha', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'gesvoip', ['Portados'])

        # Adding model 'Tarifa'
        db.create_table('tarifa', (
            ('id_tarifa', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('compania', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gesvoip.Compania'], db_column='compania')),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('valor_normal', self.gf('django.db.models.fields.FloatField')()),
            ('valor_reducido', self.gf('django.db.models.fields.FloatField')()),
            ('valor_nocturno', self.gf('django.db.models.fields.FloatField')()),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('id_ingreso', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'gesvoip', ['Tarifa'])

        # Adding model 'Usuarios'
        db.create_table('usuarios', (
            ('id_usuario', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('usuario', self.gf('django.db.models.fields.TextField')()),
            ('password', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('nombre', self.gf('django.db.models.fields.TextField')()),
            ('apellido', self.gf('django.db.models.fields.TextField')()),
            ('correo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('rol', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'gesvoip', ['Usuarios'])


    def backwards(self, orm):
        # Deleting model 'Cdr'
        db.delete_table('cdr')

        # Deleting model 'Compania'
        db.delete_table('compania')

        # Deleting model 'DetFactura'
        db.delete_table('det_factura')

        # Deleting model 'Factura'
        db.delete_table('factura')

        # Deleting model 'Feriado'
        db.delete_table('feriado')

        # Deleting model 'Horario'
        db.delete_table('horario')

        # Deleting model 'Ido'
        db.delete_table('ido')

        # Deleting model 'LogLlamadas'
        db.delete_table('log_llamadas')

        # Deleting model 'Numeracion'
        db.delete_table('numeracion')

        # Deleting model 'NumeracionAmpliada'
        db.delete_table('numeracion_ampliada')

        # Deleting model 'Portados'
        db.delete_table('portados')

        # Deleting model 'Tarifa'
        db.delete_table('tarifa')

        # Deleting model 'Usuarios'
        db.delete_table('usuarios')


    models = {
        u'gesvoip.cdr': {
            'Meta': {'object_name': 'Cdr', 'db_table': "'cdr'"},
            'compania': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fecha': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'gesvoip.compania': {
            'Meta': {'object_name': 'Compania', 'db_table': "'compania'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entidad': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id_compania': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rut': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'gesvoip.detfactura': {
            'Meta': {'object_name': 'DetFactura', 'db_table': "'det_factura'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'destino': ('django.db.models.fields.IntegerField', [], {}),
            'duracion': ('django.db.models.fields.FloatField', [], {}),
            'factura': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Factura']", 'db_column': "'factura'"}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'hora': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'horario': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id_detalle': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'origen': ('django.db.models.fields.IntegerField', [], {}),
            'tarifa': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Tarifa']", 'db_column': "'tarifa'"}),
            'valor': ('django.db.models.fields.FloatField', [], {})
        },
        u'gesvoip.factura': {
            'Meta': {'object_name': 'Factura', 'db_table': "'factura'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'fecha_fin': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fecha_inicio': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id_factura': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'tarifa': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Usuarios']", 'db_column': "'usuario'"}),
            'valor_nocturno': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'valor_normal': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'valor_reducido': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'gesvoip.feriado': {
            'Meta': {'object_name': 'Feriado', 'db_table': "'feriado'"},
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'id_feriado': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'gesvoip.horario': {
            'Meta': {'object_name': 'Horario', 'db_table': "'horario'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'dia': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fin': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'gesvoip.ido': {
            'Meta': {'object_name': 'Ido', 'db_table': "'ido'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'gesvoip.logllamadas': {
            'Meta': {'object_name': 'LogLlamadas', 'db_table': "'log_llamadas'"},
            'ani_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'compania_ani': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'compania_cdr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'connect_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dialed_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fecha': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'}),
            'hora': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id_log': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ingress_duration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'motivo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'gesvoip.numeracion': {
            'Meta': {'object_name': 'Numeracion', 'db_table': "'numeracion'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'rango': ('django.db.models.fields.IntegerField', [], {}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zona': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gesvoip.numeracionampliada': {
            'Meta': {'object_name': 'NumeracionAmpliada', 'db_table': "'numeracion_ampliada'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {}),
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id_numeracion': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'numeracion': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'gesvoip.portados': {
            'Meta': {'object_name': 'Portados', 'db_table': "'portados'"},
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'ido': ('django.db.models.fields.IntegerField', [], {}),
            'numero': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tipo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'gesvoip.tarifa': {
            'Meta': {'object_name': 'Tarifa', 'db_table': "'tarifa'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'id_ingreso': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id_tarifa': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'valor_nocturno': ('django.db.models.fields.FloatField', [], {}),
            'valor_normal': ('django.db.models.fields.FloatField', [], {}),
            'valor_reducido': ('django.db.models.fields.FloatField', [], {})
        },
        u'gesvoip.usuarios': {
            'Meta': {'object_name': 'Usuarios', 'db_table': "'usuarios'"},
            'apellido': ('django.db.models.fields.TextField', [], {}),
            'correo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id_usuario': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.TextField', [], {}),
            'password': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rol': ('django.db.models.fields.TextField', [], {}),
            'usuario': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['gesvoip']