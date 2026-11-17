import django_filters
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalog.models import Category, Equipment
from .forms import BookingForm
from .models import Booking
from .services import available_units, calc_price


class EquipmentFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="Поиск")
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    price_max = django_filters.NumberFilter(
        field_name="tariff__day_price", lookup_expr="lte")

    class Meta:
        model = Equipment
        fields = ["q", "category", "price_max"]

    def filter_q(self, qs, name, value):
        return qs.filter(Q(name__icontains=value) | Q(description__icontains=value))


def catalog(request):
    qs = Equipment.objects.exclude(condition="retired").select_related(
        "category", "tariff")
    flt = EquipmentFilter(request.GET, queryset=qs)
    page = Paginator(flt.qs, 12).get_page(request.GET.get("page"))
    return render(request, "catalog/list.html",
                  {"page": page, "filter": flt})


@login_required
@require_POST
def create_booking(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)
    form = BookingForm(request.POST)
    if not form.is_valid():
        return render(request, "rentals/booking_form.html",
                      {"form": form, "equipment": equipment}, status=400)

    date_from, date_to = form.cleaned_data["date_from"], form.cleaned_data["date_to"]
    if available_units(equipment, date_from, date_to) < 1:
        return render(request, "rentals/booking_form.html", {
            "form": form, "equipment": equipment,
            "error": "На выбранные даты нет свободных единиц"}, status=409)

    booking = form.save(commit=False)
    booking.client = request.user
    booking.equipment = equipment
    booking.total_price = calc_price(equipment, date_from, date_to)
    booking.save()
    return redirect("my_bookings")


@login_required
def my_bookings(request):
    bookings = (Booking.objects.filter(client=request.user)
                .select_related("equipment").order_by("-created_at"))
    # помечаем просроченные выдачи
    for b in bookings:
        if b.status == Booking.Status.ISSUED:
            rental = getattr(b, "rental", None)
            if rental and rental.due_date < timezone.localdate():
                b.status = Booking.Status.OVERDUE
                b.save(update_fields=["status"])
    return render(request, "rentals/my_bookings.html", {"bookings": bookings})
