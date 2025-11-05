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
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name or self.user.username

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
    participants = models.ManyToManyField('Profile', blank=True, related_name="projects")
    def __str__(self): return self.title

class Task(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks")
    title=models.CharField(max_length=200)
    status=models.CharField(max_length=50,default="OPEN")
    assignee=models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,blank=True)
    due_date=models.DateField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

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
