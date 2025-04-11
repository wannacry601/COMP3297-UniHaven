from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from .models import House
from .models import Landlord
from django.utils import timezone

class LoginTest(TestCase):
    def setUp(self):
       self.client = Client()
    
    def test_login(self):
        urlprefix = "http://127.0.0.1:8000"

        loginData = {
            "username": "groupk",
            "password": "12345678"
        }

        response = self.client.post("/login/",data=loginData)
        self.assertEqual(response.status_code, 200)
        
class HouseAPITest(TestCase):
    def setUp(self):
        self.landlord = Landlord.objects.create(
            name="yuxuan",
            phone_number="12345678"
        )
        self.house = House.objects.create(
            name="Test",
            type="mini-hall",
            rent=6000,
            location="xxx",
            beds = 2, # Number of beds
            bedrooms = 1, # Number of bedrooms
            description = "1",
            available_from=timezone.now(),
            available_to=timezone.now()+timezone.timedelta(days=1),
            landlord=self.landlord
        )
        self.client = APIClient()
        
    def test_get_house_list(self):
        response = self.client.get("list?format=json")
        print("Status Code:", response.status_code)
        #print("Response Data:", response.json())  
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        
    def test_get_house_detail(self):
        response = self.client.get(f'house/{self.house.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test')

