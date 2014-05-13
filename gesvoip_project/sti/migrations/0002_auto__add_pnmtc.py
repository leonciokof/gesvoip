# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PnMtc'
        db.create_table('pn_mtc', (
            ('ip_empresa', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('rut_propietario', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('numero_telefono', self.gf('django.db.models.fields.CharField')(max_length=12, primary_key=True)),
            ('tipo_servicio', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('modalidad', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('deuda_vencida', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=5, blank=True)),
            ('estado', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('id_documento', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('tipo_servicio_especial', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sti', ['PnMtc'])


    def backwards(self, orm):
        # Deleting model 'PnMtc'
        db.delete_table('pn_mtc')


    models = {
        u'sti.ccaa': {
            'Meta': {'object_name': 'Ccaa', 'db_table': "'ccaa'"},
            'concecionaria': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fecha_fact': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fecha_fin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fecha_inicio': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'horario': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_ccaa': ('django.db.models.fields.IntegerField', [], {}),
            'monto': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_factura': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'periodo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'trafico': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sti.cdr': {
            'Meta': {'object_name': 'Cdr', 'db_table': "'cdr'"},
            'ani_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fecha': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fecha_cdr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'final_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'hora': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_log': ('django.db.models.fields.IntegerField', [], {}),
            'idd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ingress_duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sti.centroslocales': {
            'Meta': {'object_name': 'CentrosLocales', 'db_table': "'centros_locales'"},
            'cod_centro_local': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'cod_empresa': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'desp_centro_local': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'sti.companias': {
            'Meta': {'object_name': 'Companias', 'db_table': "'companias'"},
            'cod_empresa': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iddido': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'sti.lineas': {
            'Meta': {'object_name': 'Lineas', 'db_table': "'lineas'"},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'comentarios': ('django.db.models.fields.CharField', [], {'max_length': '9999', 'blank': 'True'}),
            'comuna': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'numero': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tipo_persona': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'sti.pnmtc': {
            'Meta': {'object_name': 'PnMtc', 'db_table': "'pn_mtc'"},
            'deuda_vencida': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '5', 'blank': 'True'}),
            'estado': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id_documento': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ip_empresa': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'modalidad': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'numero_telefono': ('django.db.models.fields.CharField', [], {'max_length': '12', 'primary_key': 'True'}),
            'rut_propietario': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'tipo_servicio': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tipo_servicio_especial': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sti']