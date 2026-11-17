from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField("Категория", max_length=100, unique=True)
    # спорт / туризм / стройка — наполняется через админку

    def __str__(self):
        return self.name


class Tariff(models.Model):
    """Цена за сутки + правила штрафа."""
    name = models.CharField(max_length=100)
    day_price = models.DecimalField(
        "Цена за сутки", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    deposit = models.DecimalField(
        "Залог", max_digits=10, decimal_places=2, default=0
    )
    fine_day_percent = models.PositiveIntegerField(
        "% от суточной цены за каждый день просрочки", default=50
    )
    damage_penalty_percent = models.PositiveIntegerField(
        "Штраф за повреждение, % от залога", default=100
    )


class Equipment(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", "Новое"
        OK = "ok", "Исправно"
        REPAIR = "repair", "В ремонте"
        RETIRED = "retired", "Списано"

    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name="equipment")
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT)
    name = models.CharField("Наименование", max_length=150)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="equipment/", blank=True, null=True)
    condition = models.CharField(max_length=10, choices=Condition.choices,
                                 default=Condition.NEW)
    total_units = models.PositiveIntegerField("Всего единиц", default=0)

    class Meta:
        indexes = [models.Index(fields=["category", "condition"])]

    def __str__(self):
        return f"{self.name} ({self.category})"


class StockUnit(models.Model):
    """Физическая единица инвентаря — так ведётся склад."""
    class Status(models.TextChoices):
        AVAILABLE = "available", "На складе"
        RENTED = "rented", "Выдана"
        REPAIR = "repair", "В ремонте"
        RETIRED = "retired", "Списана"

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE,
                                  related_name="units")
    inventory_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.AVAILABLE)
    note = models.CharField("Примечание (состояние, дефекты)",
                            max_length=255, blank=True)
