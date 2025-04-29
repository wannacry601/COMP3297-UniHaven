from datetime import datetime
from tkinter.constants import CASCADE
from django.utils import timezone
from django.db import models
from rest_framework.authtoken.models import Token

# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name

class Landlord(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    student_id = models.BigIntegerField(primary_key=True) #University ID, e.g. 3035999999
    phone_number = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='students')
    def __str__(self):
        return self.name

class Specialist(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='specialists')
    def __str__(self):
        return self.name

class House(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE)

    room_number = models.CharField(max_length=20, blank=True)
    flat_number = models.CharField(max_length=20)
    floor_number = models.CharField(max_length=20)
    geo_address = models.CharField(max_length=255)

    rent = models.PositiveIntegerField() # Rent per month
    latitude = models.FloatField(default=0.00000)
    longitude = models.FloatField(default=0.00000)
    beds = models.PositiveIntegerField() # Number of beds
    bedrooms = models.PositiveIntegerField() # Number of bedrooms
    available_from = models.DateField() # Available time period
    available_to = models.DateField() # Available time period
    description = models.TextField() # Description of the house
    MC = models.FloatField(default=0.0) # Distance to Main Campus
    SRC = models.FloatField(default=0.0) # Distance to Sassoon Road Campus
    SIMS = models.FloatField(default=0.0) # Distance to Swire Institude of Marine Science
    KC = models.FloatField(default=0.0) # Distance to Kadoorie Centre
    FoD = models.FloatField(default=0.0) # Distance to Faculty of Dentistry
    HKUST = models.FloatField(default=0.0)  # Distance to HKUST Main Campus
    CUHK = models.FloatField(default=0.0)  # Distance to CUHK Main Campus

    universities = models.ManyToManyField(University, through='HouseUniversity', related_name='houses')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room_number', 'flat_number', 'floor_number', 'geo_address'],
                name='unique_house_address'
            )
        ]
    
    def getLocation(self):
        import sys
        assert "requests" in sys.modules, "Required package 'requests' is not installed. Can't fetch location from API.\nInstall the package and try again."
        
        import requests
        response = requests.get(url="https://www.als.gov.hk/lookup",
                                headers={
                                    "Accept": "application/json",
                                    "Accept-Language": "en"
                                },
                                params={
                                    "q": self.name,
                                    "t": 60,
                                })
        latitude = response.json()["SuggestedAddress"][0]["Address"]["PremisesAddress"]["GeospatialInformation"]["Latitude"]
        longitude = response.json()["SuggestedAddress"][0]["Address"]["PremisesAddress"]["GeospatialInformation"]["Longitude"]
        
        return latitude, longitude

    def getDistance(self):
        def Equirectangular(start:tuple, dst:tuple):
            import math
            x = (start[0]-dst[0]) * math.cos((start[1] + dst[1]) / 2)
            y = start[1] - dst[1]
            return round(math.sqrt(pow(x,2) + pow(y,2) * 6378), 4)
        destinations = [
            (22.28405, 114.13784), # Main Campus
            (22.2675, 114.12881), # Seassoon Road Campus
            (22.20805, 114.26021), # Swire Institude of Marine Science
            (22.43022, 114.11429), # Kadoorie Centre
            (22.28649, 114.14426), # Faculty of Dentistry
            (22.33584, 114.26355), # HKUST Campus
            (22.41907, 114.20693) # CUHK Campus
        ]

        latitude = float(self.latitude)
        longitude = float(self.longitude)
        return (Equirectangular((latitude, longitude), destinations[0]),
                Equirectangular((latitude, longitude), destinations[1]),
                Equirectangular((latitude, longitude), destinations[2]),
                Equirectangular((latitude, longitude), destinations[3]),
                Equirectangular((latitude, longitude), destinations[4]),
                Equirectangular((latitude, longitude), destinations[5]),
                Equirectangular((latitude, longitude), destinations[6]))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.latitude, self.longitude = self.getLocation()
            self.MC, self.SRC, self.SIMS, self.KC, self.FoD, self.HKUST, self.CUHK = self.getDistance()
        super(House, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class HouseUniversity(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('house', 'university')
    def __str__(self):
        return f"{self.house.name} - {self.university.name}"

class Reservation(models.Model):
    choices = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=100, choices=choices) # Status of the reservation
    period_from = models.DateField() # Reservation period
    period_to = models.DateField() # Reservation period
    student = models.ForeignKey(Student, on_delete=models.CASCADE) # Student who made the reservation
    manager = models.ForeignKey(Specialist, on_delete=models.CASCADE) # Specialist who managed the reservation
    house_id = models.ForeignKey(House, on_delete=models.CASCADE) # House being reserved
    create_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.create_date = datetime.now(tz=timezone.get_current_timezone())
        if not self.status: 
            self.status = 'Pending'
        super(Reservation, self).save(*args, **kwargs)

    def __str__(self):
        return f"Reservation by {self.student.name} for {self.house_id.name} from {self.period_from} to {self.period_to}.\nSpecialist manager: {self.manager.name}"

class Rating(models.Model):
    score = models.DecimalField(max_digits=2,decimal_places=1,default=0.0)
    comment = models.TextField()
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rating {self.score}/5.0 for {self.house.name} by {self.student.name}"



class UniversityToken(models.Model):
    token = models.OneToOneField(Token, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.university.name} - {self.token.key}"