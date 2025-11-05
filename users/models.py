from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
	ROLE_CHOICES = [
		('ADMIN','Admin'),('TEAM','Team'),('ARTIST','Artist'),
		('PROD','Producer'),('MERCH','Merchandiser'),('LOC','Location'),
	]
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='TEAM')