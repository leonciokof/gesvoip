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
    pass


admin.site.register(models.Ccaa, CcaaAdmin)
admin.site.register(models.Cdr, CdrAdmin)
admin.site.register(models.CentrosLocales, CentrosLocalesAdmin)
admin.site.register(models.Companias, CompaniasAdmin)
admin.site.register(models.Lineas, LineasAdmin)
