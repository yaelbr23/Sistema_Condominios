from django.contrib import admin
from .models import t_invitaciones, t_accesos_log

@admin.register(t_invitaciones)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = ('id','f_invitado_nombre','f_apartamento','f_host','f_inicio','f_fin','f_estado','f_token')
    search_fields = ('f_invitado_nombre','f_token','f_apartamento__f_numero',
                     'f_apartamento__f_edificio__f_nombre','f_host__f_nombres','f_host__f_apellidos')
    list_filter = ('f_estado',)
    readonly_fields = ('f_creado_en','f_actualizado_en','f_token')
    list_select_related = ('f_host','f_apartamento','f_apartamento__f_edificio','f_apartamento__f_edificio__f_condominio')
    list_per_page = 50

@admin.register(t_accesos_log)
class AccesoLogAdmin(admin.ModelAdmin):
    list_display = ('id','f_invitacion','f_resultado','f_detalle','f_creado_en')
    list_filter = ('f_resultado',)
    search_fields = ('f_invitacion__f_invitado_nombre','f_invitacion__f_token')
    readonly_fields = ('f_creado_en','f_actualizado_en')
    list_select_related = ('f_invitacion',)
    list_per_page = 50