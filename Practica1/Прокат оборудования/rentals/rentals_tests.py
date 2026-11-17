from datetime import date
from decimal import Decimal

from django.test import TestCase

from catalog.models import Category, Equipment, Tariff
from rentals.services import calc_price, calc_overdue_fine


class OverlapAndPriceTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Туризм")
        self.tariff = Tariff.objects.create(name="Базовый",
                                            day_price=Decimal("500.00"))
        self.eq = Equipment.objects.create(name="Палатка 4-местная",
                                           category=self.cat, tariff=self.tariff,
                                           total_units=3)

    def test_price_three_days(self):
        self.assertEqual(calc_price(self.eq, date(2026, 6, 1), date(2026, 6, 3)),
                         Decimal("1500.00"))

    def test_week_discount(self):
        # 8 дней × 500 − 10% = 3600
        self.assertEqual(calc_price(self.eq, date(2026, 6, 1), date(2026, 6, 8)),
                         Decimal("3600.00"))

    def test_overdue_fine(self):
        from unittest.mock import MagicMock
        rental = MagicMock()
        rental.due_date = date(2026, 6, 10)
        rental.returned_at = None
        rental.booking.equipment.tariff.day_price = Decimal("500.00")
        rental.booking.equipment.tariff.fine_day_percent = 50
        # 3 дня просрочки × 50% от 500 = 750
        self.assertEqual(calc_overdue_fine(rental), Decimal("750.00"))
