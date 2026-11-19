from django.test import  TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta

from .models import Category, Equipment, Booking

class BookinkTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        self.category = Category.objects.create(
            name='Спортивное оборудование'
        )
        
        self.equipment = Equipment.objects.create(
            name='Велосипед',
            category=self.category,
            description='Горный велосипед',
            price_per_day=500,
            quantity=1
        )
        
    def test_booking_price(self):
        days = 3
        price = 500
        
        total = days * price
        
        self.assertEqual(total, 1500)
        
    def test_booking_overlap(self):
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=3)
        
        Booking.objects.create(
            user=self.user,
            equipment=self.equipment,
            start_date=start,
            end_date=end,
            total_price=1500,
            status='confirmed'
        )
        
        overLapping = Booking.objects.filter(
            equipment=self.equipment,
            status='confirmed',
            start_date__lt=end,
            end_date__gt=start
            ).exists()
        
        self.assertTrue(overLapping)
        
        