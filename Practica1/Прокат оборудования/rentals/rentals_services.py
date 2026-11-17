from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from .models import Booking, Fine, Rental

# Статусы, при которых бронь реально занимает инвентарь
ACTIVE_STATUSES = [Booking.Status.PENDING, Booking.Status.CONFIRMED,
                   Booking.Status.ISSUED, Booking.Status.OVERDUE]


def available_units(equipment, date_from: date, date_to: date) -> int:
    """Сколько единиц свободно в интервале [date_from, date_to].

    Интервалы пересекаются, если start_a < end_b и start_b < end_a.
    Точная проверка пересечения — по ней пишем тесты.
    """
    busy = Booking.objects.filter(
        equipment=equipment, status__in=ACTIVE_STATUSES,
        date_from__lt=date_to,          # чужая бронь началась раньше нашего конца
        date_to__gte=date_from,         # и закончилась не раньше нашего начала
    ).values_list("unit_id", flat=True) if False else None  # unit появляется в Rental
    # Реальная логика: считаем, сколько единиц занято пересекающимися арендами
    rented_units = Rental.objects.filter(
        booking__equipment=equipment,
        booking__status__in=[Booking.Status.ISSUED, Booking.Status.OVERDUE],
        returned_at__isnull=True,
    ).count()
    # Плюс единицы, удерживаемые подтверждёнными бронями на эти даты:
    confirmed = Booking.objects.filter(
        equipment=equipment, status=Booking.Status.CONFIRMED,
        date_from__lt=date_to, date_to__gte=date_from,
    ).count()
    repair = equipment.units.filter(status="repair").count()
    retired = equipment.units.filter(status="retired").count()
    free_total = equipment.total_units - repair - retired
    return max(free_total - rented_units - confirmed, 0)


def calc_price(equipment, date_from: date, date_to: date) -> Decimal:
    days = (date_to - date_from).days + 1
    price = equipment.tariff.day_price * days
    # скидка за срок от 7 дней — пример бизнес-правила
    if days >= 7:
        price *= Decimal("0.9")
    return price.quantize(Decimal("0.01"))


def calc_overdue_fine(rental: Rental) -> Decimal:
    """Штраф: % от суточной цены за каждый день просрочки."""
    if rental.returned_at:
        last_day = rental.returned_at.date()
    else:
        last_day = timezone.localdate()
    days_late = (last_day - rental.due_date).days
    if days_late <= 0:
        return Decimal("0")
    day_price = rental.booking.equipment.tariff.day_price
    percent = rental.booking.equipment.tariff.fine_day_percent
    return (day_price * Decimal(percent) / Decimal(100) * days_late).quantize(Decimal("0.01"))


def close_rental(rental: Rental, condition: str, is_damaged: bool):
    """Приём оборудования: закрываем аренду, начисляем штрафы, меняем склад."""
    rental.returned_at = timezone.now()
    rental.condition_on_return = condition
    rental.is_damaged = is_damaged
    rental.booking.status = Booking.Status.RETURNED
    rental.booking.save(update_fields=["status"])
    rental.save(update_fields=["returned_at", "condition_on_return", "is_damaged"])

    # единица инвентаря возвращается на склад (или в ремонт)
    rental.unit.status = "repair" if is_damaged else "available"
    rental.unit.save(update_fields=["status"])

    overdue = calc_overdue_fine(rental)
    if overdue > 0:
        Fine.objects.create(rental=rental, reason=Fine.Reason.OVERDUE, amount=overdue)
    if is_damaged:
        deposit = rental.booking.equipment.tariff.deposit
        penalty = deposit * rental.booking.equipment.tariff.damage_penalty_percent / 100
        if penalty > 0:
            Fine.objects.create(rental=rental, reason=Fine.Reason.DAMAGE,
                                amount=Decimal(penalty).quantize(Decimal("0.01")))
