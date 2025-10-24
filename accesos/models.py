from django.db import models
from django.db.models import Q, F
from catalogo.models import TimeStampedActiveModel, t_apartamentos
from usuarios.models import t_residentes
import secrets

class InvitacionEstado(models.TextChoices):
    PENDIENTE = 'PEND', 'Pendiente'
    USADA     = 'USED', 'Usada'
    CANCELADA = 'CANC', 'Cancelada'
    VENCIDA   = 'EXPD', 'Vencida'

class t_invitaciones(TimeStampedActiveModel):
    f_host = models.ForeignKey(t_residentes, on_delete=models.PROTECT, related_name='invitaciones')
    f_apartamento = models.ForeignKey(t_apartamentos, on_delete=models.PROTECT, related_name='invitaciones')
    f_invitado_nombre = models.CharField(max_length=120)
    f_invitado_doc = models.CharField(max_length=32, blank=True, default='')
    f_inicio = models.DateTimeField()
    f_fin = models.DateTimeField()
    f_estado = models.CharField(max_length=4, choices=InvitacionEstado.choices,
                                default=InvitacionEstado.PENDIENTE, db_index=True)
    f_token = models.CharField(max_length=64, unique=True, db_index=True, blank=True, default='')
    f_usada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_invitaciones'
        ordering = ['-f_creado_en']
        constraints = [
            models.CheckConstraint(check=Q(f_fin__gt=F('f_inicio')), name='ck_inv_ventana_valida'),
        ]
        indexes = [
            models.Index(fields=['f_apartamento', 'f_estado']),
            models.Index(fields=['f_host', 'f_estado']),
        ]

    def __str__(self):
        return f"{self.f_invitado_nombre} → {self.f_apartamento} [{self.get_f_estado_display()}]"

    def save(self, *args, **kwargs):
        # Genera token único si está vacío
        if not self.f_token:
            self.f_token = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)

class AccesoResultado(models.TextChoices):
    OK        = 'OK', 'Válido'
    EXPIRADA  = 'EXP', 'Expirada'
    CANCELADA = 'CAN', 'Cancelada'
    INVALIDA  = 'INV', 'Inválida'

class t_accesos_log(TimeStampedActiveModel):
    f_invitacion = models.ForeignKey(t_invitaciones, on_delete=models.PROTECT, related_name='logs')
    f_resultado = models.CharField(max_length=3, choices=AccesoResultado.choices)
    f_detalle = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        db_table = 't_accesos_log'
        ordering = ['-f_creado_en']

    def __str__(self):
        return f"{self.f_invitacion} -> {self.get_f_resultado_display()}"