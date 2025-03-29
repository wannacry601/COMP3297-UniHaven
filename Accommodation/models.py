from django.db import models

# Create your models here.
class Landlord(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.BigIntegerField(primary_key=True) #University ID, e.g. 3035999999
    phone_number = models.CharField(max_length=100)

class Specialist(models.Model):
    name = models.CharField(max_length=100)


class House(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE)
    rent = models.IntegerField() # Rent per month
    location = models.CharField(max_length=100)
    beds = models.IntegerField() # Number of beds
    bedrooms = models.IntegerField() # Number of bedrooms
    available = models.DurationField() # Available time period




