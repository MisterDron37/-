from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import date

from .models import Equipment, Booking, RentalRecord
from .forms import BookingForm

def catalog(request):
    equipments = Equipment.objects.filter(condition='good')

    search = request.GET.get('search', '')
    categories = request.GET.get('categories', '')

    if search:
        equipments = Equipment.filter(name__icontains=search)

    if categories:
        equipments = Equipment.filter(category_id= categories)

    return render(request, 'catalog.html', {'equipments': equipments})

    @login_required
    def create_booking(request, equipment_id):
        equipment = get_object_or_404(
            Equipment,
            id=equipment_id,
            condition='good'
        )

        if request.method == 'POST':
            form = BookingFrom(request.POST)

            if form.is_valid():
                start = form.cleaned_data['start_date']
                end = From.cleaned_data['end_date']

                if start < date.today():
                    form.add_error(
                    'start_date',
                    'нельзя бронировать прошедшие даты.'
                    )

                else:
                    with transaction.atomic():
                        equipment = Equipment.objects.select_for_update().get(id=equipment_id)

                        overlapping = Booking.object.filter(
                            equipment=equipment,
                            status__in=[
                                'pending', 'confirmed', 'issued'
                            ],
                            start_date__lt=end,
                            end_date__gt=start
                        ).count()

                        if overlapping >= equipment.quantity:
                            form.add_error(
                                None,
                                'На выбранные даты оборудование недоступно.'
                            )

                        else:
                            days = (end - start).days
                            total = days * equipment.price_per_day

                            booking = form.save(commit=False)
                            booking.user = request.user
                            booking.equipment = equipment
                            booking.total_price = total
                            booking.save()

                            return redirect('profile')

        else:
            form = BookingFrom()

        return render(request, 'booking.html', {
            'form' : form,
            'equipment': equipment,
        })

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_date')

    return render(request, 'profile.html', {'bookings': bookings})

def is_manager(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_manager)
def manager_panel(request):
    bookings = Booking.objects.exclude(
        status__in=['returned', 'cancelled']
    )

    return render(request, 'manager.html', {'bookings': bookings})

@login_required
@user_passes_test(is_manager)
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST' and booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()

    return redirect('manager')

@login_required
@user_passes_test(is_manager)
def issue_equiipment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST' and booking.status == 'confirmed':
        RentalRecord.objects.get_or_create(
            booking=booking,
            defaults={
                'issue_condition': 'Оборудование выдано в исправном состоянии',
                'issue_date': timezone.localdate(),
            }
        )

        booking.status = 'issued'
        booking.save()

        return redirect('manager')

    @login_required
    @user_passes_test(is_manager)
    def return_equipment(request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if request.method == 'POST' and booking.status == 'issued':
            record = get_object_or_404(
                RentalRecord,
                booking=booking
            )

            record.return_condition = request.POST.get(
                'condition', 'Состояние не указано'
            )

            record.return_date = timezone.localdate()

            if record.return_date > booking.end_date:
                overdue_days = (
                    record.return_date - booking.end_date
                ).days

                record.fine = overdue_days * booking.equipment.price_per_day

            record.save()

            booking.status = 'returned'
            booking.save()

    return redirect('manager')

@login_required
@user_passes_test(is_manager)
def statistics(request):
    total_bookings = Booking.objects.count()

    revenue = Booking.objects.filter(
        status__in=['returned', 'issued']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'statistics.html', {
        'total_bookings': total_bookings,
        'revenue': revenue,
    })