from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import *
import json

class HouseTestCase(APITestCase):
    def setUp(self):
        self.HKU = University.objects.create(
            name="HKU"
        )
        self.CUHK = University.objects.create(
            name = "CUHK"
        )
        self.HKUSuperuser = User.objects.create_superuser(
            username="HKUadmin",
            email="admin@test.hku.hk",
            password="adminpassword"
        )
        self.CUHKSuperuser = User.objects.create_superuser(
            username="CUHKadmin",
            email="admin@test.cuhk.hk",
            password="adminpassword"
        )
        self.HKUToken, created = Token.objects.get_or_create(user=self.HKUSuperuser)
        self.HKU_Token = UniversityToken.objects.create(
            token = self.HKUToken,
            university = self.HKU
        )
        self.CUHKToken, created = Token.objects.get_or_create(user=self.CUHKSuperuser)
        self.CUHK_Token = UniversityToken.objects.create(
            token = self.CUHKToken,
            university = self.CUHK
        )
        self.house1 = House.objects.create(
                    name="House 1",
                    type="Apartment",
                    landlord=Landlord.objects.create(
                        name="Yuxuan",
                        phone_number="123456789"
                    ),
                    room_number="1",
                    flat_number="C",
                    floor_number="3",
                    geo_address="Jolly Villa",
                    rent=3000,
                    beds=2,
                    bedrooms=1,
                    available_from="2025-03-01",
                    available_to="2025-08-31",
                    description="A cozy apartment near the university.",
                )
        self.house1.universities.set([self.HKU])

        self.house2 = House.objects.create(
                    name="House 2",
                    type="Studio",
                    landlord=Landlord.objects.create(
                        name="Xiaobang",
                        phone_number="123456789"
                    ),
                    room_number="0",
                    flat_number="G",
                    floor_number="22",
                    geo_address="South View Garden",
                    rent=5000,
                    beds=2,
                    bedrooms=2,
                    available_from="2025-04-01",
                    available_to="2025-10-31",
                    description="A cozy apartment near the university.",
                )
        self.house2.universities.set([self.HKU])

        self.house3 = House.objects.create(
                    name="House 3",
                    type="Apartment",
                    landlord=Landlord.objects.create(
                        name="Kay",
                        phone_number="123456789"
                    ),
                    room_number="3",
                    flat_number="E",
                    floor_number="12",
                    geo_address="Glen Haven",
                    rent=12000,
                    beds=4,
                    bedrooms=3,
                    available_from="2025-01-01",
                    available_to="2025-12-31",
                    description="A cozy apartment near the university.",
                )
        self.house3.universities.set([self.HKU,self.CUHK])

        self.house4 = House.objects.create(
                    name="House 4",
                    type="Apartment",
                    landlord=Landlord.objects.create(
                        name="Katie",
                        phone_number="123456789"
                    ),
                    room_number="0",
                    flat_number="D",
                    floor_number="2",
                    geo_address="Prosperity Mansion",
                    rent=5000,
                    beds=2,
                    bedrooms=1,
                    available_from="2025-03-15",
                    available_to="2025-07-31",
                    description="A cozy apartment near the university.",
                )
        self.house4.universities.set([self.CUHK])

        self.specialist1 = Specialist.objects.create(
            name="Anson Lee",
            email="specialist1@test.hku.hk",
            phone_number="22904324",
            university=self.HKU,
        )
        self.specialist2 = Specialist.objects.create(
            name="Candy Chan",
            email="specialist2@test.hku.hk",
            phone_number="35286925",
            university=self.HKU,
        )
        self.specialist3 = Specialist.objects.create(
            name="Billy Johnson",
            email="specialist3@test.cuhk.hk",
            phone_number="39101481",
            university=self.CUHK,
        )
        self.specialist4 = Specialist.objects.create(
            name="Fred Lam",
            email="specialist4@test.hku.hk",
            phone_number="38594679",
            university=self.HKU
        )
        
    
    def test_house_retrieve(self):
        """
        Test the retrievement of a house.
        """
        request = self.client.get(f'/house/{self.house1.pk}/', headers={"Authorization": f"Token {self.HKUToken.key}"})
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['name'], self.house1.name)
        self.assertEqual(response_data['type'], self.house1.type)
        # self.assertEqual(response_data['landlord'], self.landlord.id)
        self.assertEqual(response_data['room_number'], self.house1.room_number)
        self.assertEqual(response_data['flat_number'], self.house1.flat_number)
        self.assertEqual(response_data['floor_number'], self.house1.floor_number)
        self.assertEqual(response_data['geo_address'], self.house1.geo_address)
        self.assertEqual(response_data['rent'], self.house1.rent)
        self.assertEqual(response_data['beds'], self.house1.beds)
        self.assertEqual(response_data['bedrooms'], self.house1.bedrooms)
        self.assertEqual(response_data['available_from'], self.house1.available_from)
        self.assertEqual(response_data['available_to'], self.house1.available_to)
        self.assertEqual(response_data['description'], self.house1.description)
    
    def test_house_modify(self):
        """
        Test the modification of a house.
        """
        data = {
            "name": "Updated House",
            "type": "Updated Type",
            "landlord": Landlord.objects.create(
                name="George",
                phone_number="12344555"
            ).pk,
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
        request = self.client.post(f'/house/{self.house1.pk}/', data=data)
        self.assertEqual(request.status_code, 200)
        self.house1.refresh_from_db()
        self.assertEqual(self.house1.name, data['name'])
        self.assertEqual(self.house1.type, data['type'])
        self.assertEqual(self.house1.room_number, data['room_number'])
        self.assertEqual(self.house1.flat_number, data['flat_number'])
        self.assertEqual(self.house1.floor_number, data['floor_number'])
        self.assertEqual(self.house1.geo_address, data['geo_address'])
        self.assertEqual(self.house1.rent, data['rent'])
        self.assertEqual(self.house1.beds, data['beds'])
        self.assertEqual(self.house1.bedrooms, data['bedrooms'])
        self.assertEqual(str(self.house1.available_from), str(data['available_from']))
        self.assertEqual(str(self.house1.available_to), str(data['available_to']))
        self.assertEqual(self.house1.description, data['description'])
    
class HouseListTestCase(APITestCase):
    def setUp(self):
        self.HKU = University.objects.create(
            name="HKU"
        )
        self.CUHK = University.objects.create(
            name="CUHK"
        )
        self.HKUSuperuser = User.objects.create_superuser(
            username="HKUadmin",
            email="admin@test.hku.hk",
            password="adminpassword"
        )
        self.CUHKSuperuser = User.objects.create_superuser(
            username="CUHKadmin",
            email="admin@test.cuhk.hk",
            password="adminpassword"
        )
        self.HKUToken, created = Token.objects.get_or_create(user=self.HKUSuperuser)
        self.HKU_Token = UniversityToken.objects.create(
            token=self.HKUToken,
            university=self.HKU
        )
        self.CUHKToken, created = Token.objects.get_or_create(user=self.CUHKSuperuser)
        self.CUHK_Token = UniversityToken.objects.create(
            token=self.CUHKToken,
            university=self.CUHK
        )
        self.house1 = House.objects.create(
            name="House 1",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Yuxuan",
                phone_number="123456789"
            ),
            room_number="1",
            flat_number="C",
            floor_number="3",
            geo_address="Jolly Villa",
            rent=3000,
            beds=2,
            bedrooms=1,
            available_from="2025-03-01",
            available_to="2025-08-31",
            description="A cozy apartment near the university.",
        )
        self.house1.universities.set([self.HKU])

        self.house2 = House.objects.create(
            name="House 2",
            type="Studio",
            landlord=Landlord.objects.create(
                name="Xiaobang",
                phone_number="123456789"
            ),
            room_number="0",
            flat_number="G",
            floor_number="22",
            geo_address="South View Garden",
            rent=5000,
            beds=2,
            bedrooms=2,
            available_from="2025-04-01",
            available_to="2025-10-31",
            description="A cozy apartment near the university.",
        )
        self.house2.universities.set([self.HKU])

        self.house3 = House.objects.create(
            name="House 3",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Kay",
                phone_number="123456789"
            ),
            room_number="3",
            flat_number="E",
            floor_number="12",
            geo_address="Glen Haven",
            rent=12000,
            beds=4,
            bedrooms=3,
            available_from="2025-01-01",
            available_to="2025-12-31",
            description="A cozy apartment near the university.",
        )
        self.house3.universities.set([self.HKU, self.CUHK])

        self.house4 = House.objects.create(
            name="House 4",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Katie",
                phone_number="123456789"
            ),
            room_number="0",
            flat_number="D",
            floor_number="2",
            geo_address="Prosperity Mansion",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2025-03-15",
            available_to="2025-07-31",
            description="A cozy apartment near the university.",
        )
        self.house4.universities.set([self.CUHK])

        self.landlord = Landlord.objects.create(
            name="New landlord",
            phone_number="11111111"
        )
    
    def test_house_create(self):
        """
        Test the creation of a house.
        """
        data = {
            "name": "New House",
            "type": "Apartment",
            "landlord": self.landlord.pk,
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

        request = self.client.post('/house_universities/', data={"house_id": house.pk, "university_id": self.HKU.pk})
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
        
        request = self.client.post('/house_universities/', data={"house_id": house2.id, "university_id": self.CUHK.id})
        self.assertEqual(request.status_code, 201)
    
    def test_house_list_retrieve(self):
        """
        Test the retrievement of a list of houses.
        """
        # Test the list view
        # data = {
        #     "university_id": self.university.id, 
        #     "format": "json",
        # }
        headers = {
            'Authorization': f'Token {self.HKUToken.key}',
        }
        request = self.client.get('/list/', headers=headers)
        self.assertEqual(request.status_code, 200)
        
        headers = {
            'Authorization': f'Token {self.CUHKToken.key}',
        }
        request = self.client.get('/list/', headers=headers)
        self.assertEqual(request.status_code, 200)
    
    def test_houst_list_retrieve_filter(self):
        """
        Test the retrievement of a list of houses with filter.
        """
        house1 = House.objects.create(
            name="Another House 1",
            type="Apartment",
            landlord=self.landlord,
            room_number="3",
            flat_number="A",
            floor_number="7",
            geo_address="Yip Cheung Building",
            rent=3000,
            beds=1,
            bedrooms=1,
            available_from="2025-12-01",
            available_to="2026-12-01",
            description="A spacious apartment near the university.",
        )
        house2 = House.objects.create(
            name="Another House 2",
            type="Studio",
            landlord=self.landlord,
            room_number="2",
            flat_number="B",
            floor_number="8",
            geo_address="Knowles Building",
            rent=8000,
            beds=3,
            bedrooms=2,
            available_from="2025-07-01",
            available_to="2025-12-31",
            description="A luxurious apartment near the university.",
        )
        house3 = House.objects.create(
            name="Another House 3",
            type="Single Room",
            landlord=self.landlord,
            room_number="4",
            flat_number="C",
            floor_number="9",
            geo_address="Centennial Campus",
            rent=20000,
            beds=6,
            bedrooms=5,
            available_from="2024-12-01",
            available_to="2026-12-01",
            description="A modern apartment near the university.",
        )
        house1.universities.set([self.HKU])
        house2.universities.set([self.HKU])
        house3.universities.set([self.HKU])
        
        # Test the list view with filter
        headers = {
            "Authorization": f"Token {self.HKUToken.key}",
        }
        
        data = {
            "type": ["Studio"],
        }
        request = self.client.get('/list/', data=data, headers=headers)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "price": ["<5000"],
        }
        request = self.client.get('/list/', data=data, headers=headers)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "bedrooms": ["1"],
        }
        request = self.client.get('/list/', data=data, headers=headers)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "beds": ["3"],
        }
        request = self.client.get('/list/', data=data, headers=headers)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "location": "Avalon",
        }
        request = self.client.get('/list/', data=data)
        self.assertEqual(request.status_code, 404)
        
        # sort by rent
        data = {
            "order_by": "rent",
        }
        request = self.client.get('/list/', data=data, headers=headers)
        self.assertEqual(request.status_code, 200)

class ReservationTestCase(APITestCase):
    def setUp(self):
        self.HKU = University.objects.create(
            name="HKU"
        )
        self.CUHK = University.objects.create(
            name="CUHK"
        )
        self.HKUSuperuser = User.objects.create_superuser(
            username="HKUadmin",
            email="admin@test.hku.hk",
            password="adminpassword"
        )
        self.CUHKSuperuser = User.objects.create_superuser(
            username="CUHKadmin",
            email="admin@test.cuhk.hk",
            password="adminpassword"
        )
        self.HKUToken, created = Token.objects.get_or_create(user=self.HKUSuperuser)
        self.HKU_Token = UniversityToken.objects.create(
            token=self.HKUToken,
            university=self.HKU
        )
        self.CUHKToken, created = Token.objects.get_or_create(user=self.CUHKSuperuser)
        self.CUHK_Token = UniversityToken.objects.create(
            token=self.CUHKToken,
            university=self.CUHK
        )
        self.house1 = House.objects.create(
            name="House 1",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Yuxuan",
                phone_number="123456789"
            ),
            room_number="1",
            flat_number="C",
            floor_number="3",
            geo_address="Jolly Villa",
            rent=3000,
            beds=2,
            bedrooms=1,
            available_from="2025-03-01",
            available_to="2025-08-31",
            description="A cozy apartment near the university.",
        )
        self.house1.universities.set([self.HKU])

        self.house2 = House.objects.create(
            name="House 2",
            type="Studio",
            landlord=Landlord.objects.create(
                name="Xiaobang",
                phone_number="123456789"
            ),
            room_number="0",
            flat_number="G",
            floor_number="22",
            geo_address="South View Garden",
            rent=5000,
            beds=2,
            bedrooms=2,
            available_from="2025-04-01",
            available_to="2025-10-31",
            description="A cozy apartment near the university.",
        )
        self.house2.universities.set([self.HKU])

        self.house3 = House.objects.create(
            name="House 3",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Kay",
                phone_number="123456789"
            ),
            room_number="3",
            flat_number="E",
            floor_number="12",
            geo_address="Glen Haven",
            rent=12000,
            beds=4,
            bedrooms=3,
            available_from="2025-01-01",
            available_to="2025-12-31",
            description="A cozy apartment near the university.",
        )
        self.house3.universities.set([self.HKU, self.CUHK])

        self.house4 = House.objects.create(
            name="House 4",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="Katie",
                phone_number="123456789"
            ),
            room_number="0",
            flat_number="D",
            floor_number="2",
            geo_address="Prosperity Mansion",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2025-03-15",
            available_to="2025-07-31",
            description="A cozy apartment near the university.",
        )
        self.house4.universities.set([self.CUHK])

        self.student = Student.objects.create(
            name="Yuxuan",
            phone_number="123456789",
            email="sora@connect.hku.hk",
            student_id=3035999999,
            university=self.HKU
        )
        self.student2 = Student.objects.create(
            name="Xiaobang",
            phone_number="123456789",
            email="test@connect.hku.hk",
            student_id=3035999998,
            university=self.HKU
        )
        self.student3 = Student.objects.create(
            name="yuanshen",
            phone_number="123456789",
            email="yuanshen@test.cuhk.hk",
            student_id=3035999997,
            university=self.CUHK
        )
        
        self.specialist1 = Specialist.objects.create(
            name="Anson Lee",
            email="specialist1@test.hku.hk",
            phone_number="22904324",
            university=self.HKU,
        )
        self.specialist2 = Specialist.objects.create(
            name="Candy Chan",
            email="specialist2@test.hku.hk",
            phone_number="35286925",
            university=self.HKU,
        )
        self.specialist3 = Specialist.objects.create(
            name="Billy Johnson",
            email="specialist3@test.cuhk.hk",
            phone_number="39101481",
            university=self.CUHK,
        )
        self.specialist4 = Specialist.objects.create(
            name="Fred Lam",
            email="specialist4@test.hku.hk",
            phone_number="38594679",
            university=self.HKU
        )
        
        self.reservation1 = Reservation.objects.create(
            house_id=self.house2,
            period_from="2025-04-15",
            period_to="2025-04-21",
            student=self.student,
            manager=self.specialist1,
            status="Confirmed",
        )
        self.reservation2 = Reservation.objects.create(
            house_id=self.house1,
            period_from="2025-04-22",
            period_to="2025-05-14",
            student=self.student,
            manager=self.specialist1,
            status="Confirmed",
        )
        self.reservation4 = Reservation.objects.create(
            house_id=self.house3,
            period_from="2025-05-22",
            period_to="2025-07-07",
            student=self.student2,
            manager=self.specialist2,
            status="Confirmed"
        )
        self.reservation5 = Reservation.objects.create(
            house_id=self.house3,
            period_from="2025-03-01",
            period_to="2025-05-07",
            student=self.student3,
            manager=self.specialist3,
            status="Confirmed"
        )
    
    
    def test_reservation_create(self):
        """
        Test the creation of a reservation.
        """
        new_student = Student.objects.create(
                name="New Student",
                phone_number="123456789",
                email="new@test.hku.hk",
                student_id=3035999996,
                university=self.HKU
            )
        data = {
            "house_id" : self.house1.pk,
            "period_from" : "2025-06-15",
            "period_to" : "2025-06-30",
            "student" : new_student.student_id,
            "manager" : self.specialist1.id,
        }
        request = self.client.put('/reservation/', data=data)
        self.assertEqual(request.status_code, 201)
        
        reservation = Reservation.objects.filter(house_id=self.house1.id).latest("create_date")
        self.assertEqual(reservation.student, new_student)
        self.assertEqual(reservation.manager, self.specialist1)
        self.assertEqual(str(reservation.period_from), str(data['period_from']))
        self.assertEqual(str(reservation.period_to), str(data['period_to']))
        self.assertEqual(reservation.status, "Pending")
    
    def test_reservation_student_retrieve(self):
        """
        Test the retrievement of a reservation for a student.
        """     
        data = {
            "identity": "student",
            "id": self.student.student_id, 
            "format": "json",
        }
        request = self.client.get('/reservation/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        # self.assertEqual(response_data['house_id'], self.house.id)
        # self.assertEqual(response_data['period_from'], str(reservation.period_from))
        # self.assertEqual(response_data['period_to'], str(reservation.period_to))
        # self.assertEqual(response_data['manager'], sefl.specialist1.id)
        # self.assertEqual(response_data['status'], reservation.status)
        
    def test_reservation_specialist_retrieve(self):
        """
        Test the retrievement of a reservation for a specialist.
        """       
        data = {
            "identity": "specialist",
            "id": self.specialist1.id, 
            "format": "json",
        }
        request = self.client.get('/reservation/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        # self.assertEqual(response_data['house_id'], self.house.id)
        # self.assertEqual(response_data['period_from'], str(reservation.period_from))
        # self.assertEqual(response_data['period_to'], str(reservation.period_to))
        # self.assertEqual(response_data['student'], self.student.student_id)
        # self.assertEqual(response_data['status'], reservation.status)
        
    def test_reservation_student_cancel(self):
        """
        Test the cancellation of a reservation by a student.
        """
        data = {
            "identity": "student",
            "id": self.student.student_id, 
            "reservation_id": self.reservation1.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 400)
    
    def test_reservation_specialist_cancel(self):
        """
        Test the cancellation of a reservation by a specialist.
        """
        reservation = Reservation.objects.create(
            house_id=self.house1,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist1
        )
        
        data = {
            "identity": "specialist",
            "id": self.specialist1.id, 
            "reservation_id": reservation.id,
            "action": "cancel",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 200)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "Cancelled")
        
        data = {
            "identity": "specialist",
            "id": self.specialist1.id, 
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
            house_id=self.house1,
            period_from="2023-10-01",
            period_to="2024-10-01",
            student=self.student,
            manager=self.specialist1
        )
        
        data = {
            "identity": "specialist",
            "id": self.specialist1.id, 
            "reservation_id": reservation.id,
            "action": "confirm",
        }
        request = self.client.post('/reservation/', data=data)
        self.assertEqual(request.status_code, 200)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "Confirmed")
        
        data = {
            "identity": "specialist",
            "id": self.specialist1.id, 
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
        
class HouseUniversityTestCase(APITestCase):
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
        self.house = House.objects.create(
            name="New House",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="John Doe",
                phone_number="123456789"
            ),
            room_number="Room 101",
            flat_number="Flat 1A",
            floor_number="5th",
            geo_address="Posco Building",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2024-10-01",
            available_to="2025-10-01",
            description="A cozy apartment near the university.",
        )
        
    def test_house_university_create(self):
        """
        Test the creation of a house-university relationship.
        """
        data = {
            "house_id": self.house.id,
            "university_id": self.university.id,
        }
        request = self.client.post('/house_universities/', data=data)
        self.assertEqual(request.status_code, 201)
        house_university = HouseUniversity.objects.get(house=self.house, university=self.university)
        self.assertEqual(house_university.house, self.house)
        self.assertEqual(house_university.university, self.university)
    
    def test_house_university_retrieve(self):
        """
        Test the retrievement of a house-university relationship.
        """
        house_university = HouseUniversity.objects.create(
            house=self.house,
            university=self.university
        )
        
        data = {
            "house_id": self.house.id,
        }
        request = self.client.get('/house_universities/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['university'], self.university.id)
        
        data = {
            "university_id": self.university.id,
        }
        request = self.client.get('/house_universities/', data=data)
        response_data = json.loads(request.content)[0]
        self.assertEqual(request.status_code, 200)
        self.assertEqual(response_data['house'], self.house.id)
    
    def test_house_university_delete(self):
        """
        Test the deletion of a house-university relationship.
        """
        house_university = HouseUniversity.objects.create(
            house=self.house,
            university=self.university
        )
        
        data = {
            "house_id": self.house.id,
            "university_id": self.university.id,
        }
        request = self.client.delete('/house_universities/', data=data)
        self.assertEqual(request.status_code, 200)
        
        with self.assertRaises(HouseUniversity.DoesNotExist):
            HouseUniversity.objects.get(house=self.house, university=self.university)

class RatingTestCase(APITestCase):
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
        self.house = House.objects.create(
            name="New House",
            type="Apartment",
            landlord=Landlord.objects.create(
                name="John Doe",
                phone_number="123456789"
            ),
            room_number="Room 101",
            flat_number="Flat 1A",
            floor_number="5th",
            geo_address="Posco Building",
            rent=5000,
            beds=2,
            bedrooms=1,
            available_from="2024-10-01",
            available_to="2025-10-01",
            description="A cozy apartment near the university.",
        )
        
        self.student = Student.objects.create(
            name="Jane Smith",
            phone_number="123456789",
            email="example@example.com",
            student_id=3035999999,
            university=self.university
        )
            
    
    def test_rating_create(self):
        """
        Test the creation of a rating.
        """
        data = {
            "house_id": self.house.id,
            "student_id": self.student.student_id,
            "score": 5,
            "comment": "Fantastic!",
        }
        request = self.client.put('/ratings/', data=data)
        self.assertEqual(request.status_code, 403)
        
        self.house.universities.set([self.university])
        
        request = self.client.put('/ratings/', data=data)
        self.assertEqual(request.status_code, 400)
        
        reservation = Reservation.objects.create(
            house_id=self.house,
            period_from="2024-10-01",
            period_to="2025-10-01",
            student=self.student,
            manager=Specialist.objects.create(
                name="Dr. Smith",
                phone_number="123456789",
                email="example@example.com",
                university=self.university
            ),
        )
        reservation.status = "Confirmed"
        reservation.save()
        
        request = self.client.put('/ratings/', data=data)
        self.assertEqual(request.status_code, 201)
        
        rating = Rating.objects.get(house=self.house, student_id=data['student_id'])
        self.assertEqual(rating.house, self.house)
        self.assertEqual(rating.student_id, data['student_id'])
        self.assertEqual(rating.score, data['score'])
        self.assertEqual(rating.comment, data['comment'])
    
    def test_rating_retrieve(self):
        """
        Test the retrievement of a rating.
        """
        rating = Rating.objects.create(
            house=self.house,
            student=self.student,
            score=1,
            comment="Err...",
        )
        data = {
            "house_id": self.house.id,
        }
        request = self.client.get('/ratings/', data=data)
        self.assertEqual(request.status_code, 200)
        
        for response_data in json.loads(request.content):
            self.assertAlmostEqual(response_data['house'], self.house.id)
            self.assertAlmostEqual(response_data['student'], self.student.student_id)
            self.assertAlmostEqual(float(response_data['score']), rating.score)
            self.assertAlmostEqual(response_data['comment'], rating.comment)
        
class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="example@example.com",
            password="adminpassword",
        )
    
    def test_login(self):
        data = {
            "username": self.user.username,
            "password": "adminpassword",
        }
        request = self.client.post('/login/', data=data)
        self.assertEqual(request.status_code, 200)
        
        data = {
            "username": "admin",
            "password": "wrongpassword",
        }
        request = self.client.post('/login/', data=data)
        self.assertEqual(request.status_code, 401)