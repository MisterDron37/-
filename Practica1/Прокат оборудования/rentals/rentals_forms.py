from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["date_from", "date_to"]
        widgets = {
            "date_from": forms.DateInput(attrs={"type": "date"}),
            "date_to": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get("date_from")
        date_to = cleaned.get("date_to")
        if date_from and date_to:
            if date_from < timezone.localdate():
                self.add_error("date_from", "Нельзя бронировать прошедшую дату")
            if date_to < date_from:
                self.add_error("date_to", "Дата возврата раньше даты выдачи")
            if (date_to - date_from).days + 1 > 30:
                self.add_error("date_to", "Максимальный срок — 30 суток")
        return cleaned
