from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Booking, Rental, StockUnit
from .services import close_rental


@staff_member_required
def manager_queue(request):
    pending = Booking.objects.filter(status=Booking.Status.PENDING)
    active = Rental.objects.select_related("booking__equipment", "unit")
    return render(request, "rentals/manager.html",
                  {"pending": pending, "active_rentals": active})


@staff_member_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id,
                                status=Booking.Status.PENDING)
    booking.status = Booking.Status.CONFIRMED
    booking.save(update_fields=["status"])
    return redirect("manager_queue")


@staff_member_required
def issue_equipment(request, booking_id):
    """Выдача: менеджер выбирает свободную единицу и фиксирует состояние."""
    booking = get_object_or_404(Booking, pk=booking_id,
                                status=Booking.Status.CONFIRMED)
    unit = booking.equipment.units.filter(status="available").first()
    if unit is None:
        return render(request, "rentals/manager.html",
                      {"error": "Нет свободных единиц на складе"}, status=409)

    condition = request.POST.get("condition", "")
    Rental.objects.create(
        booking=booking, unit=unit,
        due_date=booking.date_to,
        condition_on_issue=condition,
    )
    unit.status = StockUnit.Status.RENTED
    unit.save(update_fields=["status"])
    booking.status = Booking.Status.ISSUED
    booking.save(update_fields=["status"])
    return redirect("manager_queue")


@staff_member_required
def accept_return(request, rental_id):
    rental = get_object_or_404(Rental, pk=rental_id, returned_at__isnull=True)
    if request.method == "POST":
        close_rental(rental,
                     condition=request.POST.get("condition", ""),
                     is_damaged=bool(request.POST.get("is_damaged")))
        return redirect("manager_queue")
    return render(request, "rentals/return_form.html", {"rental": rental})
