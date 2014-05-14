from django.contrib import admin

from . import models


class CcaaAdmin(admin.ModelAdmin):
    pass


class CdrAdmin(admin.ModelAdmin):
    pass


class CentrosLocalesAdmin(admin.ModelAdmin):
    pass


class CompaniasAdmin(admin.ModelAdmin):
    pass


class LineasAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'nombre',
        'tipo_persona',
        'comentarios',
        'area',
        'comuna',
    )
    search_fields = ('numero',)


class PnMtcAdmin(admin.ModelAdmin):
    list_display = (
        'numero_telefono',
        'ip_empresa',
        'rut_propietario',
        'tipo_servicio',
        'modalidad',
        'deuda_vencida',
        'estado',
        'id_documento',
        'tipo_servicio_especial',
    )
    search_fields = ('numero_telefono',)


admin.site.register(models.Ccaa, CcaaAdmin)
admin.site.register(models.Cdr, CdrAdmin)
admin.site.register(models.CentrosLocales, CentrosLocalesAdmin)
admin.site.register(models.Companias, CompaniasAdmin)
admin.site.register(models.Lineas, LineasAdmin)
admin.site.register(models.PnMtc, PnMtcAdmin)
