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
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    status=models.CharField(max_length=50,default="PLANNED")
    created_at=models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField('Profile', blank=True, related_name="projects")
    owners = models.ManyToManyField('Profile', blank=True, related_name="owned_projects")
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
    created_at=models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
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
