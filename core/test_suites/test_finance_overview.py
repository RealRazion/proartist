from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import FinanceEntry, FinanceProject, Profile
from core.serializers import (
    DebtPaymentActionSerializer,
    FinanceProjectListSerializer,
    _debt_monthly_amount,
    _monthly_amount,
    _next_due_date,
)


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

    def test_overview_tracks_subscriptions_separately(self):
        user = get_user_model().objects.create_user(username="finance-sub-test", password="test12345")
        profile = Profile.objects.create(user=user, name="Finance Test")
        project = FinanceProject.objects.create(
            owner=profile,
            title="Budget",
            currency="EUR",
            current_balance=Decimal("1500.00"),
            monthly_savings_target=Decimal("0.00"),
            emergency_buffer_target=Decimal("0.00"),
        )
        FinanceEntry.objects.create(
            project=project,
            title="Gehalt",
            entry_type="INCOME",
            amount=Decimal("2000.00"),
            frequency="MONTHLY",
            due_date=date(2026, 5, 1),
            is_active=True,
        )
        FinanceEntry.objects.create(
            project=project,
            title="Streaming",
            category="Abo",
            entry_type="SUBSCRIPTION",
            amount=Decimal("19.99"),
            frequency="MONTHLY",
            due_day=5,
            is_active=True,
        )
        FinanceEntry.objects.create(
            project=project,
            title="Miete",
            entry_type="FIXED",
            amount=Decimal("800.00"),
            frequency="MONTHLY",
            due_day=3,
            is_active=True,
        )

        serializer = FinanceProjectListSerializer(
            project,
            context={"request": SimpleNamespace(query_params={"month": "2026-05"})},
        )
        overview = serializer.data["overview"]

        self.assertEqual(overview["monthly_subscriptions"], 19.99)
        self.assertEqual(overview["monthly_fixed_costs"], 800.0)
        self.assertEqual(overview["monthly_outflow"], 819.99)
        self.assertEqual(overview["monthly_left"], 1180.01)
        self.assertTrue(any(item["entry_type"] == "SUBSCRIPTION" for item in overview["due_soon"]))


class DebtPaymentActionSerializerTests(TestCase):
    def test_accepts_blank_reschedule_date(self):
        serializer = DebtPaymentActionSerializer(
            data={"decision": "missed", "reschedule_date": "", "notes": "offen"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNone(serializer.validated_data["reschedule_date"])

    def test_accepts_german_payment_date_format(self):
        serializer = DebtPaymentActionSerializer(
            data={"decision": "paid", "amount": "12.50", "date": "01.06.2026"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["date"], date(2026, 6, 1))
