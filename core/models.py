import uuid

from django.db import models
from django.conf import settings

ROLE_CHOICES = [
    ("TEAM","Team/Admin"),
    ("ARTIST","Artist / Rapper / Sänger"),
    ("PROD","Producer"),
    ("VIDEO","Videograf"),
    ("MERCH","Merchandiser"),
    ("MKT","Vermarktung/Managing"),
    ("LOC","Location"),
]

def _generate_system_api_key():
    return uuid.uuid4().hex

class Role(models.Model):
    key = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    def __str__(self): return self.get_key_display()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True,default="")
    roles = models.ManyToManyField(Role, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    socials = models.JSONField(default=dict, blank=True)     # {"instagram":"...", ...}
    genre = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    onboarding_uploaded_example = models.BooleanField(default=False)
    notification_settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name or self.user.username

class RegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Offen"),
        ("INVITED", "Eingeladen"),
        ("REJECTED", "Abgelehnt"),
    ]
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="OPEN")
    invite_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invited_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.email

class Example(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="examples")
    title = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    file = models.FileField(upload_to="examples/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Request(models.Model):
    TYPE_CHOICES=[("COLLAB","Collab"),("BOOK","Booking"),("OTHER","Other")]
    STATUS_CHOICES=[("OPEN","Offen"),("ACCEPTED","Angenommen"),("DECLINED","Abgelehnt")]
    sender = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="sent_requests")
    receiver = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="received_requests")
    req_type = models.CharField(max_length=20,choices=TYPE_CHOICES,default="COLLAB")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

class ChatThread(models.Model):
    a = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="threads_a")
    b = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="threads_b")
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    class Meta: ordering = ["created_at"]
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField(blank=True)  # Text
    file = models.FileField(upload_to="chat/", blank=True, null=True)  # Anhang
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
class Project(models.Model):
    PARTICIPANT_TASK_ACCESS_CHOICES = [
        ("NONE", "Keine Task-Rechte"),
        ("COMMENT", "Kommentare"),
        ("EDIT", "Tasks bearbeiten"),
    ]
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    status=models.CharField(max_length=50,default="PLANNED")
    created_at=models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField('Profile', blank=True, related_name="projects")
    owners = models.ManyToManyField('Profile', blank=True, related_name="owned_projects")
    participant_task_access = models.CharField(
        max_length=12,
        choices=PARTICIPANT_TASK_ACCESS_CHOICES,
        default="NONE",
    )
    def __str__(self): return self.title

class Task(models.Model):
    PRIORITY_CHOICES = [
        ("LOW", "Niedrig"),
        ("MEDIUM", "Mittel"),
        ("HIGH", "Hoch"),
        ("CRITICAL", "Kritisch"),
    ]
    TASK_TYPE_CHOICES = [
        ("INTERNAL", "Intern"),
        ("EXTERNAL", "Extern"),
    ]
    RECURRENCE_CHOICES = [
        ("NONE", "Keine"),
        ("DAILY", "Täglich"),
        ("WEEKLY", "Wöchentlich"),
        ("MONTHLY", "Monatlich"),
    ]
    REVIEW_STATUS_CHOICES = [
        ("REVIEWED", "Reviewed"),
        ("NOT_REVIEWED", "Nicht reviewed"),
    ]

    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks", null=True, blank=True)
    title=models.CharField(max_length=200)
    status=models.CharField(max_length=50,default="OPEN")
    due_date=models.DateField(null=True,blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES, default="EXTERNAL")
    stakeholders = models.ManyToManyField(Profile, blank=True, related_name="task_stakeholder")
    assignees = models.ManyToManyField(Profile, blank=True, related_name="assigned_tasks")
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks_created")
    updated_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks_updated")
    created_at=models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    recurrence_pattern = models.CharField(max_length=12, choices=RECURRENCE_CHOICES, default="NONE")
    recurrence_interval = models.PositiveIntegerField(default=1)
    recurrence_generated = models.BooleanField(default=False)
    recurrence_parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_recurrences",
    )
    def __str__(self): return self.title

class ProjectAttachment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_uploads")
    file = models.FileField(upload_to="project_attachments/")
    label = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.label or self.file.name

class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="task_uploads")
    file = models.FileField(upload_to="task_attachments/")
    label = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.label or self.file.name

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="task_comments")
    body = models.TextField()
    mentions = models.ManyToManyField(Profile, blank=True, related_name="mentioned_in_task_comments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return f"{self.author} -> {self.task}"

class Contract(models.Model):
    STATUS=[("DRAFT","Entwurf"),("PENDING","Ausstehend"),("ACTIVE","Aktiv"),("ENDED","Beendet")]
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="contracts")
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    rev_share = models.PositiveIntegerField(default=30)  # %
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="DRAFT")
    pdf = models.FileField(upload_to="contracts/", blank=True)

class Payment(models.Model):
    STATUS=[("DUE","Fällig"),("PAID","Bezahlt"),("FAILED","Fehlgeschlagen")]
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="payments")
    contract = models.ForeignKey(Contract,on_delete=models.CASCADE,related_name="payments", null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    period_month = models.DateField()  # z.B. 2025-11-01 (Monatsstichtag)
    status = models.CharField(max_length=10, choices=STATUS, default="DUE")
    stripe_invoice_id = models.CharField(max_length=80, blank=True)


class FinanceProject(models.Model):
    CURRENCY_CHOICES = [
        ("EUR", "Euro"),
        ("USD", "US-Dollar"),
        ("CHF", "Schweizer Franken"),
    ]

    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="finance_projects")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="EUR")
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dispo_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dispo_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_savings_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    emergency_buffer_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    savings_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Prozent vom Rest zur Seite legen (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title", "-created_at"]

    def __str__(self):
        return self.title


class FinanceMember(models.Model):
    ROLE_CHOICES = [
        ("PRIMARY", "Hauptperson"),
        ("PARTNER", "Partner"),
        ("CHILD", "Kind"),
        ("OTHER", "Weitere Person"),
    ]

    project = models.ForeignKey(FinanceProject, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="PRIMARY")
    notes = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name", "created_at"]

    def __str__(self):
        return f"{self.project.title}: {self.name}"


class FinanceEntry(models.Model):
    TYPE_CHOICES = [
        ("INCOME", "Einnahme"),
        ("FIXED", "Fixkosten"),
        ("VARIABLE", "Variable Ausgabe"),
        ("DEBT", "Schuldenrate"),
        ("SAVING", "Sparen"),
    ]
    FREQUENCY_CHOICES = [
        ("MONTHLY", "Monatlich"),
        ("WEEKLY", "Woechentlich"),
        ("YEARLY", "Jaehrlich"),
        ("ONCE", "Einmalig"),
    ]

    project = models.ForeignKey(FinanceProject, on_delete=models.CASCADE, related_name="entries")
    member = models.ForeignKey(
        FinanceMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=120, blank=True)
    entry_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default="FIXED")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=12, choices=FREQUENCY_CHOICES, default="MONTHLY")
    due_day = models.PositiveSmallIntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_shared = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["entry_type", "title", "-created_at"]

    def __str__(self):
        return self.title


class Debt(models.Model):
    """Track individual debts with payment schedules (e.g., Klarna, loans, etc.)"""
    STATUS = [
        ("ACTIVE", "Aktiv"),
        ("PAID_OFF", "Abbezahlt"),
        ("PAUSED", "Pausiert"),
    ]
    PAYMENT_TYPES = [
        ("INSTALLMENT", "Ratenzahlung"),
        ("FIXED_AMOUNT", "Fixbetrag"),
    ]
    DEBT_KINDS = [
        ("DEBT", "Schuld"),
        ("CREDIT", "Kredit"),
    ]
    
    project = models.ForeignKey(FinanceProject, on_delete=models.CASCADE, related_name="debts")
    name = models.CharField(max_length=200, help_text="z.B. Klarna, Darlehen, etc.")
    debt_kind = models.CharField(max_length=10, choices=DEBT_KINDS, default="DEBT")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default="INSTALLMENT")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Gesamtbetrag der Schulden")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Bisheriger bezahlter Betrag")
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Monatliche Zahlungsrate")
    due_day = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Tag im Monat fuer die Zahlungen (1-31)")
    next_due_date = models.DateField(null=True, blank=True, help_text="Naechster Faelligkeitstermin")
    status = models.CharField(max_length=20, choices=STATUS, default="ACTIVE")
    start_date = models.DateField()
    paid_off_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.project.title})"
    
    @property
    def remaining_amount(self):
        """Calculate remaining debt"""
        from decimal import Decimal
        total_amount = Decimal(self.total_amount or 0)
        amount_paid = Decimal(self.amount_paid or 0)
        return max(Decimal("0"), total_amount - amount_paid)
    
    @property
    def is_fully_paid(self):
        """Check if debt is fully paid"""
        from decimal import Decimal
        return self.remaining_amount <= Decimal("0")
    
    @property
    def scheduled_payment_amount(self):
        """Amount currently due for this debt type."""
        from decimal import Decimal

        remaining = self.remaining_amount
        if self.payment_type == "FIXED_AMOUNT":
            return remaining
        scheduled = Decimal(self.monthly_payment or 0)
        return min(remaining, scheduled)

    @property
    def months_remaining(self):
        """Calculate estimated months to pay off"""
        from decimal import Decimal

        if self.is_fully_paid:
            return 0
        if self.payment_type == "FIXED_AMOUNT":
            return 1
        monthly_payment = Decimal(self.monthly_payment or 0)
        if monthly_payment <= 0:
            return 0
        remaining = self.remaining_amount
        return int((remaining / monthly_payment) + (1 if remaining % monthly_payment else 0))


class DailyExpense(models.Model):
    """Track daily expenses like groceries, coffee, etc."""
    project = models.ForeignKey(FinanceProject, on_delete=models.CASCADE, related_name="daily_expenses")
    member = models.ForeignKey(
        FinanceMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_expenses",
    )
    date = models.DateField()
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=120, blank=True, help_text="z.B. Lebensmittel, Transport, Unterhaltung")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        unique_together = ["project", "date", "title", "amount"]  # Prevent duplicate entries

    def __str__(self):
        return f"{self.date}: {self.title} - {self.amount}€"


class Release(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="releases")
    title = models.CharField(max_length=200)
    planned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="PLANNED")
    links = models.JSONField(default=dict, blank=True)

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    fee_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Booking(models.Model):
    STATUS=[("APPLIED","Bewerbung"),("CONFIRMED","Bestätigt"),("CANCELLED","Abgesagt")]
    event = models.ForeignKey(Event,on_delete=models.CASCADE,related_name="bookings")
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="bookings")
    slot_time = models.CharField(max_length=80, blank=True)
    payout_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="APPLIED")

class Song(models.Model):
    STATUS = [
        ("ACTIVE", "Aktiv"),
        ("INACTIVE", "Inaktiv"),
        ("ARCHIVED", "Archiviert"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="songs")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="songs")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

class SongVersion(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField(default=1)
    file = models.FileField(upload_to="songs/", blank=True)
    notes = models.TextField(blank=True)
    is_mix_ready = models.BooleanField(default=False)
    is_master_ready = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-version_number"]

    def __str__(self): return f"{self.song.title} v{self.version_number}"


class GrowProGoal(models.Model):
    STATUS = [
        ("ACTIVE", "Aktiv"),
        ("ON_HOLD", "Pausiert"),
        ("DONE", "Erledigt"),
        ("ARCHIVED", "Archiviert"),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="growpro_goals")
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="growpro_created")
    assigned_team = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="growpro_assigned")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric = models.CharField(max_length=100, help_text="z.B. Monatliche Hörer, Streams, Follower")
    target_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=32, blank=True, help_text="z.B. Hörer, Streams, %")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="ACTIVE")
    last_logged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self): return self.title


class GrowProUpdate(models.Model):
    goal = models.ForeignKey(GrowProGoal, on_delete=models.CASCADE, related_name="updates")
    value = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="growpro_updates")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return f"{self.goal.title} @ {self.value}"

class ActivityEntry(models.Model):
    SEVERITY_CHOICES = [
        ("INFO","Info"),
        ("SUCCESS","Erfolg"),
        ("WARNING","Hinweis"),
        ("DANGER","Alarm"),
    ]
    event_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="INFO")
    actor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return f"{self.title} ({self.event_type})"


class Notification(models.Model):
    SEVERITY_CHOICES = [
        ("INFO", "Info"),
        ("SUCCESS", "Erfolg"),
        ("WARNING", "Hinweis"),
        ("DANGER", "Alarm"),
    ]
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    notification_type = models.CharField(max_length=50, default="system")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="INFO")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
    metadata = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.title}"

class NewsPost(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="news_posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

class FinanceTip(models.Model):
    TIP_TYPES = [
        ("CASHBACK", "Cashback"),
        ("DISCOUNT", "Rabattaktion"),
        ("REFERRAL", "Empfehlungspraemie"),
        ("OTHER", "Sonstiges"),
    ]

    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="finance_tips")
    title = models.CharField(max_length=200)
    body = models.TextField()
    tip_type = models.CharField(max_length=20, choices=TIP_TYPES, default="OTHER")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

class PluginGuide(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, related_name="plugin_guides")
    title = models.CharField(max_length=200)
    body = models.TextField()
    image = models.FileField(upload_to="plugin_guides/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title


class PluginGuideImage(models.Model):
    guide = models.ForeignKey(PluginGuide, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="plugin_guides/gallery/")
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return f"{self.guide_id}#{self.id}"

class AutomationRule(models.Model):
    TRIGGER_CHOICES = [
        ("TASK_STATUS", "Task Status"),
        ("TASK_DUE", "Task Frist"),
        ("GROWPRO_DUE", "GrowPro Frist"),
        ("PROJECT_STATUS", "Projekt Status"),
    ]
    ACTION_CHOICES = [
        ("NOTIFY", "Benachrichtigen"),
        ("ASSIGN", "Zuweisen"),
        ("WEBHOOK", "Webhook"),
    ]
    name = models.CharField(max_length=120)
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="automation_rules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.name

class SystemIntegration(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    api_key = models.CharField(max_length=64, unique=True, default=_generate_system_api_key)
    scopes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name
