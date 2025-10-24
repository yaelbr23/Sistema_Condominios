
from django.contrib import admin
from .models import t_residentes, t_residentes_apartamentos


class VinculoInline(admin.TabularInline):
    model = t_residentes_apartamentos
    extra = 1
    autocomplete_fields = ('f_apartamento',)
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    show_change_link = True


@admin.register(t_residentes)
class ResidenteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nombre_completo', 'documento', 'f_email', 'f_telefono_movil', 'f_activo', 'f_creado_en'
    )
    search_fields = (
        'f_nombres', 'f_apellidos', 'f_email', 'f_telefono_movil',
        'f_num_documento', 'f_usuario__username', 'f_usuario__email'
    )
    list_filter = ('f_activo', 'f_preferencia_contacto', 'f_tipo_documento')
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    autocomplete_fields = ('f_usuario',)
    list_select_related = ('f_usuario',)
    inlines = [VinculoInline]
    list_per_page = 50

    @admin.display(description='Nombre completo')
    def nombre_completo(self, obj):
        return f"{obj.f_nombres} {obj.f_apellidos}".strip()

    @admin.display(description='Documento')
    def documento(self, obj):
        return f"{obj.f_tipo_documento} {obj.f_num_documento}"


@admin.register(t_residentes_apartamentos)
class ResidenteAptoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'f_residente', 'f_apartamento', 'f_rol', 'f_es_principal', 'f_desde', 'f_hasta', 'f_activo'
    )
    list_filter = ('f_rol', 'f_es_principal', 'f_hasta', 'f_activo')
    search_fields = (
        'f_residente__f_nombres', 'f_residente__f_apellidos', 'f_residente__f_num_documento',
        'f_apartamento__f_numero', 'f_apartamento__f_edificio__f_nombre',
        'f_apartamento__f_edificio__f_condominio__f_nombre'
    )
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    autocomplete_fields = ('f_residente', 'f_apartamento')
    list_select_related = (
        'f_residente', 'f_apartamento', 'f_apartamento__f_edificio', 'f_apartamento__f_edificio__f_condominio'
    )
    date_hierarchy = 'f_desde'
    list_per_page = 50
