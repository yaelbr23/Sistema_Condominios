from django.db import models
from django.db.models.functions import Lower

# Create your models here.

class TimeStampedActiveModel(models.Model):
    f_activo = models.BooleanField(default=True)
    f_creado_en = models.DateTimeField(auto_now_add=True)
    f_actualizado_en = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
        
class t_condominios(TimeStampedActiveModel):
    f_nombre = models.CharField(max_length = 200)
    f_direccion = models.CharField(max_length=250, blank=True, default='')
    
    class Meta:
        db_table = 't_condominios'
        ordering = ['f_nombre', 'f_direccion']
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'
        constraints = [
            models.UniqueConstraint(
                Lower('f_nombre'),
                name='ux_condominio_nombre_ci'
            )
        ]
        
    def __str__(self):
        return self.f_nombre
    
class t_edificios(TimeStampedActiveModel):
    f_condominio = models.ForeignKey(t_condominios, on_delete= models.CASCADE, related_name= 'edificios')
    f_nombre = models.CharField(max_length=120)
    class Meta:
        db_table = 't_edificios'
        ordering = ['f_condominio', 'f_nombre']
        verbose_name = 'Edificio'
        verbose_name_plural = 'Edificios'
        constraints = [
            models.UniqueConstraint(fields= ['f_condominio', 'f_nombre'], name='uq_edificio_por_condominio')
            ]
    def __str__(self):
        return f"Edificio: {self.f_nombre}  | Condominio: {self.f_condominio}"
    
class t_apartamentos(TimeStampedActiveModel):
    f_edificio = models.ForeignKey(t_edificios, on_delete=models.CASCADE, related_name='apartamentos')
    f_numero = models.CharField(max_length=20)
    f_nivel= models.CharField(max_length=10, blank= True, default= '')
    
    class Meta:
        db_table = 't_apartamentos'
        ordering = ['f_edificio', 'f_numero']
        verbose_name = 'Apartamento'
        verbose_name_plural = 'Apartamentos'
        constraints = [
            models.UniqueConstraint(fields= ['f_edificio','f_numero'], name='unico_apartamento_por_edificio')
        ]
    
    def __str__(self):
        return f"Apto: {self.f_numero} | Edificio: {self.f_edificio}"