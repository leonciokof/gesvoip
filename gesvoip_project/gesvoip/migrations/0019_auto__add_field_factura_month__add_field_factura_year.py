# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Factura.month'
        db.add_column('factura', 'month',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=2, blank=True),
                      keep_default=False)

        # Adding field 'Factura.year'
        db.add_column('factura', 'year',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=4, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Factura.month'
        db.delete_column('factura', 'month')

        # Deleting field 'Factura.year'
        db.delete_column('factura', 'year')


    models = {
        u'gesvoip.cdr': {
            'Meta': {'object_name': 'Cdr', 'db_table': "'cdr'"},
            'compania': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fecha': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'blank': 'True'})
        },
        u'gesvoip.compania': {
            'Meta': {'ordering': "('nombre',)", 'object_name': 'Compania', 'db_table': "'compania'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'entidad': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id_compania': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rut': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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
            'id_detalle': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origen': ('django.db.models.fields.IntegerField', [], {}),
            'tarifa': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Tarifa']", 'db_column': "'tarifa'"}),
            'valor': ('django.db.models.fields.FloatField', [], {})
        },
        u'gesvoip.factura': {
            'Meta': {'object_name': 'Factura', 'db_table': "'factura'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'fecha_fin': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'dbtype': "'date'", 'null': 'True', 'blank': 'True'}),
            'fecha_inicio': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'dbtype': "'date'", 'null': 'True', 'blank': 'True'}),
            'id_factura': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2', 'blank': 'True'}),
            'tarifa': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'usuario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Usuarios']", 'db_column': "'usuario'"}),
            'valor_nocturno': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'dbtype': "'float'", 'null': 'True', 'blank': 'True'}),
            'valor_normal': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'dbtype': "'float'", 'null': 'True', 'blank': 'True'}),
            'valor_reducido': ('djorm_pgarray.fields.ArrayField', [], {'default': 'None', 'dbtype': "'float'", 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4', 'blank': 'True'})
        },
        u'gesvoip.feriado': {
            'Meta': {'ordering': "('fecha',)", 'object_name': 'Feriado', 'db_table': "'feriado'"},
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'id_feriado': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'gesvoip.horario': {
            'Meta': {'object_name': 'Horario', 'db_table': "'horario'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'dia': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fin': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'gesvoip.ido': {
            'Meta': {'ordering': "('codigo',)", 'object_name': 'Ido', 'db_table': "'ido'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'id_log': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingress_duration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'motivo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'gesvoip.numeracion': {
            'Meta': {'object_name': 'Numeracion', 'db_table': "'numeracion'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rango': ('django.db.models.fields.IntegerField', [], {}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zona': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gesvoip.numeracionampliada': {
            'Meta': {'object_name': 'NumeracionAmpliada', 'db_table': "'numeracion_ampliada'"},
            'codigo': ('django.db.models.fields.IntegerField', [], {}),
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'id_numeracion': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numeracion': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'gesvoip.portados': {
            'Meta': {'object_name': 'Portados', 'db_table': "'portados'"},
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ido': ('django.db.models.fields.IntegerField', [], {}),
            'numero': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'tipo': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'gesvoip.tarifa': {
            'Meta': {'object_name': 'Tarifa', 'db_table': "'tarifa'"},
            'compania': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gesvoip.Compania']", 'db_column': "'compania'"}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'id_ingreso': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id_tarifa': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'valor_nocturno': ('django.db.models.fields.FloatField', [], {}),
            'valor_normal': ('django.db.models.fields.FloatField', [], {}),
            'valor_reducido': ('django.db.models.fields.FloatField', [], {})
        },
        u'gesvoip.usuarios': {
            'Meta': {'object_name': 'Usuarios', 'db_table': "'usuarios'"},
            'apellido': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'correo': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id_usuario': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'rol': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'usuario': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['gesvoip']