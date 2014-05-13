# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ccaa'
        db.create_table('ccaa', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_ccaa', self.gf('django.db.models.fields.IntegerField')()),
            ('periodo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('concecionaria', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('n_factura', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('fecha_inicio', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fecha_fin', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fecha_fact', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('horario', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('trafico', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('monto', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sti', ['Ccaa'])

        # Adding model 'Cdr'
        db.create_table('cdr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_log', self.gf('django.db.models.fields.IntegerField')()),
            ('ani_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ingress_duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('final_number', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fecha_cdr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('estado', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('idd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('hora', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('fecha', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sti', ['Cdr'])

        # Adding model 'CentrosLocales'
        db.create_table('centros_locales', (
            ('cod_empresa', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('cod_centro_local', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('desp_centro_local', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'sti', ['CentrosLocales'])

        # Adding model 'Companias'
        db.create_table('companias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iddido', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cod_empresa', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'sti', ['Companias'])

        # Adding model 'Lineas'
        db.create_table('lineas', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('numero', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('tipo_persona', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('comentarios', self.gf('django.db.models.fields.CharField')(max_length=9999, blank=True)),
            ('area', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('comuna', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal(u'sti', ['Lineas'])


    def backwards(self, orm):
        # Deleting model 'Ccaa'
        db.delete_table('ccaa')

        # Deleting model 'Cdr'
        db.delete_table('cdr')

        # Deleting model 'CentrosLocales'
        db.delete_table('centros_locales')

        # Deleting model 'Companias'
        db.delete_table('companias')

        # Deleting model 'Lineas'
        db.delete_table('lineas')


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
        }
    }

    complete_apps = ['sti']