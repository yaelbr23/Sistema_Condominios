from django.contrib import admin
from .models import t_condominios,t_edificios, t_apartamentos

class ApartamentoInline(admin.TabularInline):
    model = t_apartamentos
    extra = 1

# Inline for t_edificios in t_condominios admin
class EdificioInline(admin.TabularInline):
    model = t_edificios
    extra = 1

# Register your models here.
@admin.register(t_condominios) 
class CondominioAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_nombre', 'f_direccion', 'f_activo', 'f_creado_en')
    search_fields = ('f_nombre',)
    list_filter = ('f_activo',)
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    inlines = [EdificioInline]
    

@admin.register(t_edificios)
class EdificioAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_nombre', 'f_condominio', 'f_activo', 'f_creado_en')
    list_filter = ('f_condominio', 'f_activo')
    search_fields = ('f_nombre', 'f_condominio__f_nombre')
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    list_select_related = ('f_condominio',)
    inlines = [ApartamentoInline]
    
@admin.register(t_apartamentos)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_numero', 'f_edificio', 'f_nivel', 'f_activo', 'f_creado_en')
    list_filter = ('f_edificio', 'f_activo')
    search_fields = ('f_numero', 'f_edificio__f_nombre', 'f_edificio__f_condominio__f_nombre')
    readonly_fields = ('f_creado_en', 'f_actualizado_en')
    autocomplete_fields = ('f_edificio',)
    list_select_related = ('f_edificio', 'f_edificio__f_condominio')
