from django.db import models
from django.conf import settings
from django.db.models import Q
from catalogo.models import TimeStampedActiveModel
from catalogo.models import t_apartamentos

class DocTipo(models.TextChoices):
    CEDULA = 'CED', 'Cédula'
    PASAPORTE = 'PAS', 'Pasaporte'

class PrefContacto(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'

class RolResidencia(models.TextChoices):
    OWNER = 'OWNER', 'Propietario'
    CO_OWNER = 'CO_OWNER', 'Copropietario'
    TENANT = 'TENANT', 'Inquilino'
    FAMILY = 'FAMILY', 'Familiar'
    GUEST = 'GUEST', 'Huésped'

# Create your models here.
class t_residentes(TimeStampedActiveModel):
    f_usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='residente')
    f_nombres = models.CharField(max_length=80)
    f_apellidos = models.CharField(max_length=80)
    f_tipo_documento = models.CharField(max_length=3, choices=DocTipo.choices)
    f_num_documento = models.CharField(max_length=32, db_index=True)
    f_fecha_nacimiento = models.DateField(null=True, blank=True)
    f_nacionalidad = models.CharField(max_length=60, blank=True, default='')
    f_email = models.EmailField()
    f_telefono_movil = models.CharField(max_length=20)
    f_telefono_alt = models.CharField(max_length=20, blank=True, default='')
    f_preferencia_contacto = models.CharField(max_length=9, choices=PrefContacto.choices, default=PrefContacto.EMAIL)
    f_foto = models.ImageField(upload_to='residentes/', null=True, blank=True)
    f_observaciones = models.TextField(blank=True, default='')

    class Meta:
        db_table = 't_residentes'
        verbose_name = 'Residente'
        verbose_name_plural = 'Residentes'
        ordering = ['f_nombres', 'f_apellidos']
        constraints = [
            models.UniqueConstraint(fields=['f_tipo_documento', 'f_num_documento'], name='ux_residente_doc')
        ]

    def __str__(self):
        nombre = (self.f_nombres or '').strip()
        apellidos = (self.f_apellidos or '').strip()
        full = (nombre + ' ' + apellidos).strip()
        if full:
            return full
        try:
            return self.f_usuario.get_username()
        except Exception:
            return f"Residente {self.pk}"


# New model for resident-apartment links
class t_residentes_apartamentos(TimeStampedActiveModel):
    f_residente = models.ForeignKey('t_residentes', on_delete=models.CASCADE, related_name='vinculos')
    f_apartamento = models.ForeignKey(t_apartamentos, on_delete=models.PROTECT, related_name='residentes')
    f_es_principal = models.BooleanField(default=True)
    f_desde = models.DateField()
    f_hasta = models.DateField(null=True, blank=True)
    f_rol = models.CharField(max_length=10, choices=RolResidencia.choices, default=RolResidencia.OWNER)
    f_porcentaje_copropiedad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    f_contrato_numero = models.CharField(max_length=40, blank=True, default='')
    f_contrato_desde = models.DateField(null=True, blank=True)
    f_contrato_hasta = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 't_residentes_apartamentos'
        verbose_name = 'Vínculo Residente–Apartamento'
        verbose_name_plural = 'Vínculos Residente–Apartamento'
        ordering = ['f_apartamento', 'f_residente']
        constraints = [
            models.UniqueConstraint(fields=['f_residente', 'f_apartamento'], name='uq_residente_apartamento'),
            models.UniqueConstraint(fields=['f_apartamento'], condition=Q(f_es_principal=True, f_hasta__isnull=True), name='uq_un_principal_activo_por_apto'),
            models.CheckConstraint(
                name='ck_tenant_contrato',
                check=(~Q(f_rol='TENANT') | (Q(f_contrato_desde__isnull=False) & Q(f_contrato_hasta__isnull=False)))
            ),
            models.CheckConstraint(
                name='ck_coprop_gt0_when_set',
                check=(Q(f_porcentaje_copropiedad__isnull=True) | Q(f_porcentaje_copropiedad__gt=0))
            ),
        ]

    def __str__(self):
        estado = 'activo' if self.f_hasta is None else f'hasta {self.f_hasta}'
        return f"{self.f_residente} en {self.f_apartamento} ({estado})"