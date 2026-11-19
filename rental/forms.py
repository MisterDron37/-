from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end and start >= end:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала.")

        return cleaned_data