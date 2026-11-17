from django.db import models
from django.core.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Models):
    name = models.CharField(max_length=100)
    descripion = models.TextFiled(blank=True)


    def __str__(self):
        return self.name


    class Equimpent(models.Models):
        CONDITION_CHOICES = [
            ('good', 'Исправно')
            ('repair', 'На ремонте')
            ('damage', 'Повреждено')
            ('written_off', 'Списано')
        ]

        name = models.CharField(max_length=100)
        category = models.ForeignKey(
            Category,
            on_delete=models.PROTECT
        )
        description = models.TextFiled()
        price_per_day = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(0)]
        )
        quantity = models.PositiveIntegerField(default=1)
        image = models.URLFiled(blank=True)
        condition = models.CharField(
            max_length=20,
            choices=CONDITION_CHOICES,
            default='good'
        )

        def __str__(self):
            return self.name

        class Booking(models.Models):
            STATUS_CHOICES = [
                ('pending', 'Ожидает подтверждения')
                ('confirmed', 'Заблокировано')
                ('issued', 'Выдано')
                ('returned', 'Возвращено')
                ('overdue', 'Просрочено')
                ('cancelled', 'Отменено')
            ]

        user = models.ForeignKey(
            User,
            on_delete=models.CASEDE
        )
        equipment = models.ForeignKey(
            Equipment,
            on_delete=models.PROTECT
        )
        start_date = models.DateField()
        end_date = models.DateField()
        total_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
        )
        status = models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default='pending'
        )
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.user.username} - {self.equipment.name}"

class RentalRecord(models.Model):
    booking = models.ForeignKey(
        Booking,
    on_delete=models.CASCADE
    )
    issue_condition = models.TextField()
    return_condition = models.TextField(blake=True)
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username