from django.contrib import admin

from . import models


class CdrAdmin(admin.ModelAdmin):
    pass


class CompaniaAdmin(admin.ModelAdmin):
    pass


class DetFacturaAdmin(admin.ModelAdmin):
    pass


class FacturaAdmin(admin.ModelAdmin):
    pass


class FeriadoAdmin(admin.ModelAdmin):
    pass


class HorarioAdmin(admin.ModelAdmin):
    pass


class IdoAdmin(admin.ModelAdmin):
    pass


class LogLlamadasAdmin(admin.ModelAdmin):
    pass


class NumeracionAdmin(admin.ModelAdmin):
    pass


class NumeracionAmpliadaAdmin(admin.ModelAdmin):
    pass


class PortadosAdmin(admin.ModelAdmin):
    pass


class TarifaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha', 'tipo', 'valor_normal', 'valor_reducido', 'valor_nocturno',
        'compania', 'id_ingreso')
    list_filter = ('compania',)


class UsuariosAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Cdr, CdrAdmin)
admin.site.register(models.Compania, CompaniaAdmin)
admin.site.register(models.DetFactura, DetFacturaAdmin)
admin.site.register(models.Factura, FacturaAdmin)
admin.site.register(models.Feriado, FeriadoAdmin)
admin.site.register(models.Horario, HorarioAdmin)
admin.site.register(models.Ido, IdoAdmin)
admin.site.register(models.LogLlamadas, LogLlamadasAdmin)
admin.site.register(models.Numeracion, NumeracionAdmin)
admin.site.register(models.NumeracionAmpliada, NumeracionAmpliadaAdmin)
admin.site.register(models.Portados, PortadosAdmin)
admin.site.register(models.Tarifa, TarifaAdmin)
admin.site.register(models.Usuarios, UsuariosAdmin)
