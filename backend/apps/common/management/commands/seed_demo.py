"""Seed a demo academy with admin, coaches, players, groups, sessions, payments."""
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.academies.models import Academy
from apps.accounts.models import User, UserRole
from apps.coaches.models import Coach
from apps.players.models import Player
from apps.groups.models import Group, GroupMembership
from apps.sessions.models import Venue, SessionSeries, SessionOccurrence, SessionEnrollment
from apps.attendance.models import AttendanceRecord
from apps.payments.models import Invoice, Payment


class Command(BaseCommand):
    help = "Seed a demo academy with users and sample data."

    def handle(self, *args, **opts):
        academy, _ = Academy.objects.get_or_create(
            slug="demo",
            defaults=dict(name="Demo Academy", language="en", currency="EGP"),
        )
        admin, created = User.objects.get_or_create(
            email="admin@sams.local",
            defaults=dict(role=UserRole.ADMIN, academy=academy, is_staff=True, first_name="Demo", last_name="Admin"),
        )
        if created:
            admin.set_password("Password123!")
            admin.save()
        # ensure academy + role even if user pre-existed
        if not admin.academy_id:
            admin.academy = academy
            admin.save()

        venue, _ = Venue.objects.get_or_create(academy=academy, name="Main Field",
                                               defaults=dict(address="Cairo", capacity=40))

        coaches = []
        for fn, ln, sp in [("Ahmed", "Hassan", "Football"), ("Sara", "Ali", "Swimming")]:
            c, _ = Coach.objects.get_or_create(academy=academy, first_name=fn, last_name=ln,
                                               defaults=dict(specialty=sp))
            coaches.append(c)

        group, _ = Group.objects.get_or_create(academy=academy, name="U12 Football",
                                               defaults=dict(age_min=10, age_max=12, capacity=20,
                                                             primary_coach=coaches[0]))

        players = []
        for i in range(8):
            p, _ = Player.objects.get_or_create(
                academy=academy, first_name=f"Player{i+1}", last_name="Demo",
                defaults=dict(date_of_birth=date(2013, 1, 1), guardian_name="Guardian"),
            )
            players.append(p)
            GroupMembership.objects.get_or_create(academy=academy, group=group, player=p)

        series, _ = SessionSeries.objects.get_or_create(
            academy=academy, title="U12 Weekly Practice",
            defaults=dict(group=group, venue=venue, recurrence=SessionSeries.Recurrence.WEEKLY,
                          weekly_mask=0b0010100,  # Tue + Thu
                          start_date=date.today(), end_date=date.today() + timedelta(days=30),
                          start_time=time(17, 0), end_time=time(18, 30), capacity=20),
        )
        series.coaches.set(coaches[:1])

        # generate next 2 weeks of occurrences
        d = date.today()
        end = d + timedelta(days=14)
        while d <= end:
            if series.weekly_mask & (1 << d.weekday()):
                starts = datetime.combine(d, series.start_time)
                ends = datetime.combine(d, series.end_time)
                occ, made = SessionOccurrence.objects.get_or_create(
                    academy=academy, series=series, starts_at=starts,
                    defaults=dict(title=series.title, group=group, venue=venue,
                                  ends_at=ends, capacity=series.capacity),
                )
                if made:
                    for p in players:
                        SessionEnrollment.objects.get_or_create(academy=academy, occurrence=occ, player=p)
            d += timedelta(days=1)

        # mark some attendance on past sessions
        past = SessionOccurrence.objects.filter(academy=academy, starts_at__lt=timezone.now())[:3]
        for occ in past:
            for i, p in enumerate(players):
                AttendanceRecord.objects.update_or_create(
                    academy=academy, occurrence=occ, player=p,
                    defaults=dict(status="present" if i % 4 else "absent", marked_by=admin),
                )

        # invoices + payments
        for p in players[:5]:
            inv, _ = Invoice.objects.get_or_create(
                academy=academy, player=p, number=f"INV-{p.first_name}",
                defaults=dict(issue_date=date.today(), due_date=date.today() + timedelta(days=14),
                              subtotal=Decimal("500"), tax=Decimal("0"), total=Decimal("500"),
                              currency="EGP", status="issued"),
            )
            if p == players[0]:
                Payment.objects.get_or_create(
                    academy=academy, invoice=inv, player=p, amount=Decimal("500"),
                    received_at=timezone.now(), method="cash",
                )
                inv.status = "paid"
                inv.save()

        self.stdout.write(self.style.SUCCESS(
            "Seeded demo academy. Login: admin@sams.local / Password123!"
        ))
