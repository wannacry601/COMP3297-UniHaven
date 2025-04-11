from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Landlord(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    # student_user = models.OneToOneField(User, on_delete=models.CASCADE) # One-to-one relationship with User model
    email = models.EmailField(max_length=100)
    student_id = models.BigIntegerField(primary_key=True) #University ID, e.g. 3035999999
    phone_number = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Specialist(models.Model):
    name = models.CharField(max_length=100)
    # specialist_user = models.OneToOneField(User, on_delete=models.CASCADE) # One-to-one relationship with User model
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class House(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE)
    rent = models.PositiveIntegerField() # Rent per month
    location = models.CharField(max_length=100)
    beds = models.PositiveIntegerField() # Number of beds
    bedrooms = models.PositiveIntegerField() # Number of bedrooms
    available_from = models.DateTimeField() # Available time period
    available_to = models.DateTimeField() # Available time period
    description = models.TextField() # Description of the house
    def __str__(self):
        return self.name




