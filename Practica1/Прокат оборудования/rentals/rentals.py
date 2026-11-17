from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Забронировано (ожидает)"
        CONFIRMED = "confirmed", "Подтверждено"
        ISSUED = "issued", "Выдано"
        RETURNED = "returned", "Возвращено"
        OVERDUE = "overdue", "Просрочено"
        CANCELLED = "cancelled", "Отменено"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="bookings")
    equipment = models.ForeignKey("catalog.Equipment", on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()          # включительно
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.date_to < self.date_from:
            raise ValidationError("Дата возврата раньше даты выдачи")

    def days(self):
        return (self.date_to - self.date_from).days + 1


class Rental(models.Model):
    """Активная выдача — создаётся менеджером из подтверждённой брони."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    unit = models.ForeignKey("catalog.StockUnit", on_delete=models.PROTECT)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()                       # когда должны вернуть
    returned_at = models.DateTimeField(null=True, blank=True)
    condition_on_issue = models.CharField(max_length=255, blank=True)
    condition_on_return = models.CharField(max_length=255, blank=True)
    is_damaged = models.BooleanField(default=False)


class Fine(models.Model):
    class Reason(models.TextChoices):
        OVERDUE = "overdue", "Просрочка"
        DAMAGE = "damage", "Повреждение"
        LOSS = "loss", "Утрата"

    rental = models.ForeignKey(Rental, on_delete=models.CASCADE,
                               related_name="fines")
    reason = models.CharField(max_length=10, choices=Reason.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
