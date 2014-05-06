# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Usuarios.rol'
        db.alter_column('usuarios', 'rol', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Usuarios.apellido'
        db.alter_column('usuarios', 'apellido', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Usuarios.usuario'
        db.alter_column('usuarios', 'usuario', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Usuarios.correo'
        db.alter_column('usuarios', 'correo', self.gf('django.db.models.fields.EmailField')(max_length=75))

        # Changing field 'Usuarios.nombre'
        db.alter_column('usuarios', 'nombre', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Usuarios.password'
        db.alter_column('usuarios', 'password', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'Usuarios.rol'
        db.alter_column('usuarios', 'rol', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Usuarios.apellido'
        db.alter_column('usuarios', 'apellido', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Usuarios.usuario'
        db.alter_column('usuarios', 'usuario', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Usuarios.correo'
        db.alter_column('usuarios', 'correo', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Usuarios.nombre'
        db.alter_column('usuarios', 'nombre', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Usuarios.password'
        db.alter_column('usuarios', 'password', self.gf('django.db.models.fields.TextField')())

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
            'apellido': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'correo': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id_usuario': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rol': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'usuario': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['gesvoip']