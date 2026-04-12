from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase

from core.serializers import _monthly_amount, _next_due_date, _debt_monthly_amount


class FinanceOverviewLogicTests(TestCase):
    def test_monthly_amount_ignores_future_monthly_start(self):
        entry = SimpleNamespace(
            amount="1200.00",
            frequency="MONTHLY",
            is_active=True,
            due_date=date(2025, 5, 1),
            due_day=None,
        )
        self.assertEqual(_monthly_amount(entry, date(2025, 4, 1)), Decimal("0.00"))

    def test_weekly_next_due_date_respects_future_start_date(self):
        entry = SimpleNamespace(
            frequency="WEEKLY",
            is_active=True,
            due_date=date(2025, 5, 1),
        )
        self.assertEqual(_next_due_date(entry, date(2025, 4, 1)), date(2025, 5, 1))

    def test_yearly_next_due_date_respects_future_year(self):
        entry = SimpleNamespace(
            frequency="YEARLY",
            is_active=True,
            due_date=date(2026, 5, 1),
        )
        self.assertEqual(_next_due_date(entry, date(2025, 4, 1)), date(2026, 5, 1))

    def test_debt_monthly_amount_ignores_debt_start_after_month(self):
        debt = SimpleNamespace(
            status="ACTIVE",
            is_fully_paid=False,
            scheduled_payment_amount="250.00",
            payment_type="INSTALLMENT",
            due_day=15,
            start_date=date(2025, 5, 1),
            next_due_date=None,
        )
        self.assertEqual(_debt_monthly_amount(debt, date(2025, 4, 1)), Decimal("0.00"))
