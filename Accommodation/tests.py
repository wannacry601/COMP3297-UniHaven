from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import *
import json

class HouseTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(
            name="HW311"
        )
        self.client.force_authenticate(user=User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        ))
        
        self.token, created = Token.objects.get_or_create(user=self.client.handler._force_user)
        self.university_token = UniversityToken.objects.create(
            token=self.token,
            university=self.university
        )
            
        self.landlord = Landlord.objects.create(
            name="John Doe",
            phone_number="123456789"
        )
        self.house = House.objects.create(
            name="Sprint3",
            type="Apartment",
            landlord=self.landlord,
            room_number="Room 101",
            flat_number="Flat 1A",
            floor_number="5th",
            geo_address="Posco Building",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2023-10-01",
            available_to="2024-10-01",
            description="A cozy apartment near the university.",
        )
        self.house.universities.set([self.university])
        
    
    def test_house_retrieve(self):
        """
        Test the retrievement of a house.
        """
        request = self.client.get(f'/house/{self.house.id}/', data={"university_id": self.university.id})
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['name'], self.house.name)
        self.assertEqual(response_data['type'], self.house.type)
        self.assertEqual(response_data['landlord'], self.landlord.id)
        self.assertEqual(response_data['room_number'], self.house.room_number)
        self.assertEqual(response_data['flat_number'], self.house.flat_number)
        self.assertEqual(response_data['floor_number'], self.house.floor_number)
        self.assertEqual(response_data['geo_address'], self.house.geo_address)
        self.assertEqual(response_data['rent'], self.house.rent)
        self.assertEqual(response_data['beds'], self.house.beds)
        self.assertEqual(response_data['bedrooms'], self.house.bedrooms)
        self.assertEqual(response_data['available_from'], self.house.available_from)
        self.assertEqual(response_data['available_to'], self.house.available_to)
        self.assertEqual(response_data['description'], self.house.description)
    
    def test_house_modify(self):
        """
        Test the modification of a house.
        """
        data = {
            "name": "Updated House",
            "type": "Updated Type",
            "landlord": self.landlord.id,
            "room_number": "Room 102",
            "flat_number": "Flat 1B",
            "floor_number": "6th",
            "geo_address": "Updated Address",
            "rent": 6000,
            "beds": 3,
            "bedrooms": 2,
            "available_from": "2023-11-01",
            "available_to": "2024-11-01",
            "description": "Updated description.",
        }
        request = self.client.post(f'/house/{self.house.id}/', data=data)
        self.assertEqual(request.status_code, 200)
        self.house.refresh_from_db()
        self.assertEqual(self.house.name, data['name'])
        self.assertEqual(self.house.type, data['type'])
        self.assertEqual(self.house.room_number, data['room_number'])
        self.assertEqual(self.house.flat_number, data['flat_number'])
        self.assertEqual(self.house.floor_number, data['floor_number'])
        self.assertEqual(self.house.geo_address, data['geo_address'])
        self.assertEqual(self.house.rent, data['rent'])
        self.assertEqual(self.house.beds, data['beds'])
        self.assertEqual(self.house.bedrooms, data['bedrooms'])
        self.assertEqual(str(self.house.available_from), str(data['available_from']))
        self.assertEqual(str(self.house.available_to), str(data['available_to']))
        self.assertEqual(self.house.description, data['description'])
    
class HouseListTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(
            name="HW311"
        )
        self.client.force_authenticate(user=User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        ))
        
        self.token, created = Token.objects.get_or_create(user=self.client.handler._force_user)
        self.university_token = UniversityToken.objects.create(
            token=self.token,
            university=self.university
        )
        self.landlord = Landlord.objects.create(
            name="John Doe",
            phone_number="123456789"
        )
    
    def test_house_create(self):
        """
        Test the creation of a house.
        """
        data = {
            "name": "New House",
            "type": "Apartment",
            "landlord": self.landlord.id,
            "room_number": "Room 101",
            "flat_number": "Flat 1A",
            "floor_number": "5th",
            "geo_address": "Posco Building",
            "rent": 5000,
            "beds": 2,
            "bedrooms": 1,
            "available_from": "2023-10-01",
            "available_to": "2024-10-01",
            "description": "A cozy apartment near the university.",
        }
        request = self.client.put('/list/', data=data)
        self.assertEqual(request.status_code, 201)
        house = House.objects.get(name=data['name'])
        self.assertEqual(house.name, data['name'])
        self.assertEqual(house.type, data['type'])
        self.assertEqual(house.landlord, self.landlord)
        self.assertEqual(house.room_number, data['room_number'])
        self.assertEqual(house.flat_number, data['flat_number'])
        self.assertEqual(house.floor_number, data['floor_number'])
        self.assertEqual(house.geo_address, data['geo_address'])
        self.assertEqual(house.rent, data['rent'])
        self.assertEqual(house.beds, data['beds'])
        self.assertEqual(house.bedrooms, data['bedrooms'])
        self.assertEqual(str(house.available_from), str(data['available_from']))
        self.assertEqual(str(house.available_to), str(data['available_to']))
        self.assertEqual(house.description, data['description'])
        
        request = self.client.post('/house_universities/', data={"house_id": house.id, "university_id": self.university.id})
        self.assertEqual(request.status_code, 201)
        
        data2 = {
            "name": "New House 2",
            "type": "Apartment",
            "landlord": self.landlord.id,
            "room_number": "Room 102",
            "flat_number": "Flat 1B",
            "floor_number": "6th",
            "geo_address": "Yip Cheung Building",
            "rent": 6000,
            "beds": 3,
            "bedrooms": 2,
            "available_from": "2023-11-01",
            "available_to": "2024-11-01",
            "description": "Another cozy apartment near the university.",
        }
        request2 = self.client.put('/list/', data=data2)
        self.assertEqual(request2.status_code, 201)
        house2 = House.objects.get(name=data2['name'])
        self.assertEqual(house2.name, data2['name'])
        self.assertEqual(house2.type, data2['type'])
        self.assertEqual(house2.landlord, self.landlord)
        self.assertEqual(house2.room_number, data2['room_number'])
        self.assertEqual(house2.flat_number, data2['flat_number'])
        self.assertEqual(house2.floor_number, data2['floor_number'])
        self.assertEqual(house2.geo_address, data2['geo_address'])
        self.assertEqual(house2.rent, data2['rent'])
        self.assertEqual(house2.beds, data2['beds'])
        self.assertEqual(house2.bedrooms, data2['bedrooms'])
        self.assertEqual(str(house2.available_from), str(data2['available_from']))
        self.assertEqual(str(house2.available_to), str(data2['available_to']))
        self.assertEqual(house2.description, data2['description'])
        
        request = self.client.post('/house_universities/', data={"house_id": house2.id, "university_id": self.university.id})
        self.assertEqual(request.status_code, 201)
    
    def test_house_list_retrieve(self):
        """
        Test the retrievement of a list of houses.
        """
        house1 = House.objects.create(
            name="House 1",
            type="Apartment",
            landlord=self.landlord,
            room_number="Room 201",
            flat_number="Flat 2A",
            floor_number="7th",
            geo_address="Building A",
            rent=7000,
            beds=4,
            bedrooms=3,
            available_from="2023-12-01",
            available_to="2024-12-01",
            description="A spacious apartment near the university.",
        )
        house2 = House.objects.create(
            name="House 2",
            type="Apartment",
            landlord=self.landlord,
            room_number="Room 202",
            flat_number="Flat 2B",
            floor_number="8th",
            geo_address="Building B",
            rent=8000,
            beds=5,
            bedrooms=4,
            available_from="2023-12-01",
            available_to="2024-12-01",
            description="A luxurious apartment near the university.",
        )
        house1.universities.set([self.university])
        house2.universities.set([self.university])
        # Test the list view
        data = {
            "university_id": self.university.id, 
            "format": "json",
            }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)
    
    def test_houst_list_retrieve_filter(self):
        """
        Test the retrievement of a list of houses with filter.
        """
        house1 = House.objects.create(
            name="House 1",
            type="Apartment",
            landlord=self.landlord,
            room_number="Room 201",
            flat_number="Flat 2A",
            floor_number="7th",
            geo_address="Building A",
            rent=3000,
            beds=1,
            bedrooms=1,
            available_from="2023-12-01",
            available_to="2024-12-01",
            description="A spacious apartment near the university.",
        )
        house2 = House.objects.create(
            name="House 2",
            type="Studio",
            landlord=self.landlord,
            room_number="Room 202",
            flat_number="Flat 2B",
            floor_number="8th",
            geo_address="Building B",
            rent=8000,
            beds=3,
            bedrooms=2,
            available_from="2023-12-01",
            available_to="2024-12-01",
            description="A luxurious apartment near the university.",
        )
        house3 = House.objects.create(
            name="House 3",
            type="Single Room",
            landlord=self.landlord,
            room_number="Room 203",
            flat_number="Flat 2C",
            floor_number="9th",
            geo_address="Building C",
            rent=20000,
            beds=6,
            bedrooms=5,
            available_from="2023-12-01",
            available_to="2024-12-01",
            description="A modern apartment near the university.",
        )
        house1.universities.set([self.university])
        house2.universities.set([self.university])
        house3.universities.set([self.university])
        
        # Test the list view with filter
        data = {
            "university_id": self.university.id,
            "type": ["Studio"],
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "university_id": self.university.id,
            "price": ["<5000"],
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "university_id": self.university.id,
            "bedrooms": ["1"],
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "university_id": self.university.id,
            "beds": ["3"],
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "location": "Avalon",
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 404)
        
        # sort by rent
        data = {
            "university_id": self.university.id,
            "order_by": "rent",
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 200)

class ReservationTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(
            name="HW311"
        )
        self.client.force_authenticate(user=User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        ))
        
        self.token, created = Token.objects.get_or_create(user=self.client.handler._force_user)
        self.university_token = UniversityToken.objects.create(
            token=self.token,
            university=self.university
        )
        self.landlord = Landlord.objects.create(
            name="John Doe",
            phone_number="123456789"
        )
        self.student = Student.objects.create(
            name="Jane Smith",
            phone_number="987654321",
            email="example@example.com",
            student_id=3035999999,
            university=self.university
        )
        self.specialist = Specialist.objects.create(
            name="Dr. Smith",
            phone_number="123456789",
            email="example@example.com",
            university=self.university
        )
        
        self.house = House.objects.create(
            name="New House",
            type="Apartment",
            landlord=self.landlord,
            room_number="Room 101",
            flat_number="Flat 1A",
            floor_number="5th",
            geo_address="Posco Building",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2023-10-01",
            available_to="2024-10-01",
            description="A cozy apartment near the university.",
        )
        self.house.universities.set([self.university])
    
    def test_reservation_create(self):
        """
        Test the creation of a reservation.
        """

        data = {
            "house_id": self.house.id,
            "period_from": "2023-10-01",
            "period_to": "2024-10-01",
            "student": self.student.student_id,
            "manager": self.specialist.id,
        }
        request = self.client.put('/reservation/', data=data)
        self.assertEqual(request.status_code, 201)
        
        reservation = Reservation.objects.get(house_id=self.house.id)
        self.assertEqual(reservation.student, self.student)
        self.assertEqual(reservation.manager, self.specialist)
        self.assertEqual(str(reservation.period_from), str(data['period_from']))
        self.assertEqual(str(reservation.period_to), str(data['period_to']))
        self.assertEqual(reservation.status, "Pending")
    
    def test_reservation_student_retrieve(self):
        """
        Test the retrievement of a reservation for a student.
        """
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist
        )
        
        data = {
            "identity": "student",
            "id": self.student.student_id, 
            "format": "json",
        }
        request = self.client.get('/reservation/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['house_id'], self.house.id)
        self.assertEqual(response_data['period_from'], str(reservation.period_from))
        self.assertEqual(response_data['period_to'], str(reservation.period_to))
        self.assertEqual(response_data['manager'], self.specialist.id)
        self.assertEqual(response_data['status'], reservation.status)
        
    def test_reservation_specialist_retrieve(self):
        """
        Test the retrievement of a reservation for a specialist.
        """  
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist
        )
        
        data = {
            "identity": "specialist",
            "id": self.specialist.id, 
            "format": "json",
        }
        request = self.client.get('/reservation/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['house_id'], self.house.id)
        self.assertEqual(response_data['period_from'], str(reservation.period_from))
        self.assertEqual(response_data['period_to'], str(reservation.period_to))
        self.assertEqual(response_data['student'], self.student.student_id)
        self.assertEqual(response_data['status'], reservation.status)
        
    def test_reservation_student_cancel(self):
        """
        Test the cancellation of a reservation by a student.
        """
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist
        )
        
        data = {
            "identity": "student",
            "id": self.student.student_id, 
            "reservation_id": reservation.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 200)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "Cancelled")
        
        data = {
            "identity": "student",
            "id": self.student.student_id, 
            "reservation_id": reservation.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 400)
    
    def test_reservation_specialist_cancel(self):
        """
        Test the cancellation of a reservation by a specialist.
        """
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist
        )
        
        data = {
            "identity": "specialist",
            "id": self.specialist.id, 
            "reservation_id": reservation.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 200)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "Cancelled")
        
        data = {
            "identity": "specialist",
            "id": self.specialist.id, 
            "reservation_id": reservation.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 400)
    
    def test_reservation_specialist_confirm(self):
        """
        Test the confirmation of a reservation by a specialist.
        """
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist
        )
        
        data = {
            "identity": "specialist",
            "id": self.specialist.id, 
            "reservation_id": reservation.id,
            "action": "confirm",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 200)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "Confirmed")
        
        data = {
            "identity": "specialist",
            "id": self.specialist.id, 
            "reservation_id": reservation.id,
            "action": "confirm",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 400)

class StudentTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(
            name="HW311"
        )
        self.client.force_authenticate(user=User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        ))
        
        self.token, created = Token.objects.get_or_create(user=self.client.handler._force_user)
        self.university_token = UniversityToken.objects.create(
            token=self.token,
            university=self.university
        )
    
    def test_student_create(self):
        data = {
            "name": "Jane Smith",
            "phone_number": "123456789",
            "email": "example@example.com",
            "student_id": 3035999999,
            "university": self.university.id,
        }
        request = self.client.put('/student/', data=data)
        self.assertEqual(request.status_code, 201)
        student = Student.objects.get(student_id=data['student_id'])
        self.assertEqual(student.name, data['name'])
        self.assertEqual(student.phone_number, data['phone_number'])
        self.assertEqual(student.email, data['email'])
        self.assertEqual(student.student_id, data['student_id'])
        self.assertEqual(student.university, self.university)
        
        request = self.client.put('/student/')
        self.assertEqual(request.status_code, 400)
    
    def test_student_retrieve(self):
        student = Student.objects.create(
            name="Jane Smith",
            phone_number="123456789",
            email="example@example.com",
            student_id=3035999999,
            university=self.university
        )
        data = {
            "student_id": 3035999999,
        }
        request = self.client.get('/student/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['name'], student.name)
        self.assertEqual(response_data['phone_number'], student.phone_number)
        self.assertEqual(response_data['email'], student.email)
        self.assertEqual(response_data['university'], student.university.id)
        
        data = {
            "student_id": 3036999999,
        }
        request = self.client.get('/student/', data=data)
        self.assertEqual(request.status_code, 404)
    
    def test_student_modify(self):
        student = Student.objects.create(
            name="Jane Smith",
            phone_number="123456789",
            email="example@example.com",
            student_id=3035999999,
            university=self.university
        )
        data = {
            "name": "Updated Name",
            "student_id": 3035999999,
        }
        request = self.client.post('/student/', data=data)
        self.assertEqual(request.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.name, data['name'])
        
        # Student not found
        data = {
            "name": "Updated Name",
            "student_id": 3036999999,
        }
        request = self.client.post('/student/', data=data)
        self.assertEqual(request.status_code, 404)     
        
class AuthTokenTestCase(APITestCase):
    def setUp(self):
        self.university = University.objects.create(
            name="HW311"
        )
        self.client.force_authenticate(user=User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword"
        ))
    
    def test_token_create(self):
        data = {
            "university_id": self.university.id,
            "username": "admin",
            "password": "adminpassword",
        }
        request = self.client.post('/university_token/', data=data)
        self.assertEqual(request.status_code, 200)
        
        token = Token.objects.get(user__username=data['username'])
        self.assertEqual(token.key, json.loads(request.content)['token'])
        
        data = {
            "university_id": 999,
            "username": "admin",
            "password": "adminpassword",
        }
        request = self.client.post('/university_token/', data=data)
        self.assertEqual(request.status_code, 404)
        
        request = self.client.post('/university_token/')
        self.assertIn(request.status_code, [400, 404])