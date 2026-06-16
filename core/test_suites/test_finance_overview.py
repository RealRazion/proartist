from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Debt, DebtPayment, FinanceEntry, FinanceProject, FinanceSavingsGoal, Profile
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
        self.assertEqual(overview["monthly_debt_entries"], 0.0)
        self.assertEqual(overview["monthly_debt_tracker"], 0.0)
        self.assertEqual(overview["monthly_debt_paid_actual"], 0.0)
        self.assertEqual(overview["monthly_left_actual"], 1180.01)
        self.assertTrue(any(item["entry_type"] == "SUBSCRIPTION" for item in overview["due_soon"]))

    def test_overview_tracks_savings_goal_totals(self):
        user = get_user_model().objects.create_user(username="finance-goal-test", password="test12345")
        profile = Profile.objects.create(user=user, name="Finance Goal Test")
        project = FinanceProject.objects.create(owner=profile, title="Ziele", currency="EUR")

        FinanceSavingsGoal.objects.create(
            project=project,
            title="Fuehrerschein",
            target_amount=Decimal("3000.00"),
            current_amount=Decimal("1200.00"),
            is_completed=False,
        )
        FinanceSavingsGoal.objects.create(
            project=project,
            title="Studiengebuehr",
            target_amount=Decimal("1500.00"),
            current_amount=Decimal("1500.00"),
            is_completed=True,
        )

        serializer = FinanceProjectListSerializer(
            project,
            context={"request": SimpleNamespace(query_params={"month": "2026-05"})},
        )
        overview = serializer.data["overview"]

        self.assertEqual(overview["savings_goal_target_total"], 4500.0)
        self.assertEqual(overview["savings_goal_current_total"], 2700.0)
        self.assertEqual(overview["savings_goal_open_count"], 1)

    def test_overview_emits_alert_for_high_saldo_delta(self):
        user = get_user_model().objects.create_user(username="finance-alert-test", password="test12345")
        profile = Profile.objects.create(user=user, name="Finance Alert Test")
        project = FinanceProject.objects.create(
            owner=profile,
            title="Alert Budget",
            currency="EUR",
            current_balance=Decimal("500.00"),
        )
        FinanceEntry.objects.create(
            project=project,
            title="Gehalt",
            entry_type="INCOME",
            amount=Decimal("1200.00"),
            frequency="MONTHLY",
            due_day=1,
            is_active=True,
        )
        debt = Debt.objects.create(
            project=project,
            name="Kreditkarte",
            payment_type="INSTALLMENT",
            total_amount=Decimal("1000.00"),
            amount_paid=Decimal("100.00"),
            monthly_payment=Decimal("300.00"),
            due_day=5,
            status="ACTIVE",
            start_date=date(2026, 5, 1),
        )
        DebtPayment.objects.create(
            debt=debt,
            amount=Decimal("20.00"),
            payment_date=date(2026, 5, 10),
            notes="Teilzahlung",
        )

        serializer = FinanceProjectListSerializer(
            project,
            context={"request": SimpleNamespace(query_params={"month": "2026-05"})},
        )
        overview = serializer.data["overview"]

        self.assertTrue(any(item["code"] == "SALDO_DELTA_HIGH" for item in overview["alerts"]))


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

    def test_accepts_skip_month_decision(self):
        serializer = DebtPaymentActionSerializer(data={"decision": "skip_month"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["decision"], "skip_month")
