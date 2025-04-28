from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import GenericAPIView
from django.shortcuts import render
from django.db.models import Q
from typing import override


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import University, UniversityToken

from Accommodation.serializers import *
from Accommodation.models import *

def index(request):
    return HttpResponse("200 OK")

def login(request):
    """
    Handles user login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=401)
    return JsonResponse({"message": "Method not allowed"}, status=405)
    
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_university_token(request):
    """
    Create a token for a university.
    Requires admin permission.
    ---
    POST parameters:
      - university_id: ID of the university to associate with the token
    """
    university_id = request.data.get('university_id')
    if not university_id:
        return Response({'error': 'university_id is required'}, status=400)
        
    try:
        university = University.objects.get(id=university_id)
    except University.DoesNotExist:
        return Response({'error': 'University not found'}, status=404)
        
    token, created = Token.objects.get_or_create(user=request.user)
    
    uni_token, created = UniversityToken.objects.get_or_create(
        token=token,
        defaults={'university': university}
    )
    
    if not created:
        uni_token.university = university
        uni_token.save()
        
    return Response({
        'token': token.key,
        'university': {
            'id': university.id,
            'name': university.name
        }
    })

class StudentView(GenericAPIView):
    serializer_class = StudentSerializer
    
    @override
    def get_queryset(self, id):
        queryset = Student.objects.all().filter(student_id=id)
        return queryset
    
    def get(self, request):
        id = request.data["student_id"]
        queryset = self.get_queryset(id)
        serializer = self.serializer_class(queryset, many=True)
        if queryset:
            return JsonResponse(serializer.data, safe=False, status=200)
        else:
            return JsonResponse({"message": "Student not found", "data": request.data}, status=404)
    
    def put(self, request):
        """
        Handles PUT requests to create a new Student object.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    def post(self, request):
        """
        Handles POST requests to update an existing Student object.
        """
        student_id = request.data["student_id"]
        try:
            student = Student.objects.get(student_id=student_id)
            serializer = self.serializer_class(student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found", "data": request.data}, status=404)
        
class HouseListView(GenericAPIView):
    serializer_class = HouseSerializer
    template_name = 'Accommodation/list.html'
    
    @override
    def get_queryset(self, university_id=None):
        """
        Returns a queryset of House objects.
        Filters and sorts the queryset based on the provided parameters.
        """        
        if not university_id:
            return House.objects.none()
            
        queryset = House.objects.filter(houseuniversity__university_id=university_id)

        filter_type = self.request.GET.getlist('type')
        filter_price = self.request.GET.getlist('price')
        filter_bedrooms = self.request.GET.getlist('bedrooms')
        filter_beds = self.request.GET.getlist('beds')
        filter_location = self.request.GET.getlist('location')
        filter_available_from = self.request.GET.get('begin_date')
        filter_available_to = self.request.GET.get('end_date')
        sort = self.request.GET.get('order_by')
        
        if filter_type:
            queryset = queryset.filter(type__in=filter_type)
            
        if filter_price:
            price_filters = []
            for price_range in filter_price:
                if price_range == '<5000':
                    price_filters.append(Q(rent__lt=5000))
                elif price_range == '5000-10000':
                    price_filters.append(Q(rent__gte=5000) & Q(rent__lte=10000))
                elif price_range == '>10000':
                    price_filters.append(Q(rent__gt=10000))
            
            if price_filters:
                combined_filter = price_filters[0]
                for f in price_filters[1:]:
                    combined_filter |= f
                queryset = queryset.filter(combined_filter)
                
        if filter_bedrooms:
            bedroom_filters = []
            for bedroom_count in filter_bedrooms:
                if bedroom_count in ['1', '2', '3']:
                    bedroom_filters.append(Q(bedrooms=int(bedroom_count)))
                elif bedroom_count == '>3':
                    bedroom_filters.append(Q(bedrooms__gt=3))
            
            if bedroom_filters:
                combined_filter = bedroom_filters[0]
                for f in bedroom_filters[1:]:
                    combined_filter |= f
                queryset = queryset.filter(combined_filter)
                
        if filter_beds:
            bed_filters = []
            for bed_count in filter_beds:
                if bed_count in ['1', '2', '3']:
                    bed_filters.append(Q(beds=int(bed_count)))
                elif bed_count == '>3':
                    bed_filters.append(Q(beds__gt=3))
            
            if bed_filters:
                combined_filter = bed_filters[0]
                for f in bed_filters[1:]:
                    combined_filter |= f 
                queryset = queryset.filter(combined_filter)
                
        if filter_location:
            queryset = queryset.filter(location__in=filter_location)
            
        if filter_available_from:
            queryset = queryset.filter(available_from__lte=filter_available_from)
            
        if filter_available_to:
            queryset = queryset.filter(available_to__gte=filter_available_to)

        if sort:
            university_name = getattr(self.request, 'university_name', '')
            if university_name == 'HKUST':
                queryset = queryset.order_by('HKUST')
            elif university_name == 'CUHK':
                queryset = queryset.order_by('CUHK')
            else:
                queryset = queryset.order_by(sort)
            
        return queryset

    def get(self, request):
        """
        Handles GET requests to retrieve House objects and render the list template.
        If 'format=json' is specified, returns JSON data instead.
        """
        university_id = request.GET.get("university_id")
        if request.GET.get('format') == 'json':
            queryset = self.get_queryset(university_id)
            serializer = self.serializer_class(queryset, many=True)
            if queryset: 
                return JsonResponse(serializer.data, safe=False, status=200)
            else: 
                return JsonResponse({"message": "House list not found"}, status=404)
        
        queryset = self.get_queryset()
        houses = []
        for house in queryset:
            houses.append({
                'id': house.id,
                'name': house.name,
                'type': house.type,
                'landlord': {'name': house.landlord.name if hasattr(house, 'landlord') and house.landlord else 'Unknown'},
                'rent': house.rent,
                'location': (house.latitude, house.longitude),
                'beds': house.beds,
                'bedrooms': house.bedrooms,
                'available_from': house.available_from,
                'available_to': house.available_to,
                'description': house.description,
                'area': getattr(house, 'area', 'N/A'),
                'distance': getattr(house, 'distance', 'N/A'),
                'features': getattr(house, 'features', 'No features listed')
            })
        
        context = {
            'houses': houses,
            'total_count': len(houses),
            'showing_count': len(houses),
            'page_count': 1
        }
        
        return render(request, self.template_name, context)

    def put(self, request):
        """
        Handles POST requests to create a new House object.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

class HouseView(GenericAPIView):
    serializer_class = HouseSerializer
    template_name = 'Accommodation/detail.html'

    @override
    def get_queryset(self,house_id, university_id):
        """
        Returns a queryset of House objects filtered by house_id.
        """    
        if not university_id:
            return House.objects.none()
        
        queryset = House.objects.filter(id=house_id)
        universities = queryset.first().universities.all()
        for university in universities:
            if int(university.id) == int(university_id):
                return queryset
        return House.objects.none()

    def get(self,request,house_id):
        """
        Handles GET requests to retrieve a specific House object by house_id.
        """
        university_id = request.GET.get("university_id")
        try:
            queryset = self.get_queryset(house_id, university_id)
            if not queryset.exists():
                return JsonResponse({"message": "House not found or not accessible to your university",
                                     "request id": house_id,
                                     "uni id": university_id}, status=404)
            serializer = self.serializer_class(queryset, many=True)
            return JsonResponse(serializer.data,safe=False,status=200)
        except House.DoesNotExist:
            return JsonResponse({"message": "House not found"}, status=404)

    def post(self,request,house_id):
        """
        Handles POST requests to update a specific House object by house_id.
        """
        try:
            university_id = getattr(request, 'university_id', None)
            if university_id:
                house = House.objects.filter(
                    id=house_id,
                    houseuniversity__university_id=university_id
                ).first()
                if not house:
                    return JsonResponse({"message": "House not found or not accessible to your university"}, status=404)
            else:
                house = House.objects.get(id=house_id)
            serializer = self.serializer_class(house, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except House.DoesNotExist:
            return JsonResponse({"message": "House not found"}, status=404)
        
class ReservationView(GenericAPIView):
    serializer_class = ReservationSerializer
    
    @override
    def get_queryset(self, **kwargs):
        university_id = getattr(self.request, 'university_id', None)
        
        queryset = Reservation.objects.all()
        if university_id:
            queryset = queryset.filter(
                Q(student__university_id=university_id) | 
                Q(manager__university_id=university_id)
            )
        for key, value in kwargs.items():
            queryset = queryset.filter(**{key: value})
        return queryset

    def get(self, request):
        """
        Handles GET requests to retrieve Reservation objects.
        For students, this returns all his/her history reservations.
        For specialists, this returns all reservations he/she manages.
        Accept parameters:
        - identity: "student" or "specialist" (mandatory)
        - id: student_id or specialist_id (mandatory)
        """
        id = request.data["id"]
        if request.data['identity'] == "student": queryset = self.get_queryset(student=id)
        elif request.data['identity'] == "specialist": queryset = self.get_queryset(manager=id)
        else: return JsonResponse({"message": "Invalid identity", "Identity": request.GET.get('identity')}, status=400)
        serializer = self.serializer_class(queryset, many=True)
        if queryset:
            return JsonResponse(serializer.data, safe=False, status=200)
        else:
            return JsonResponse({"message": "Reservation list not found"}, status=404)
        
    def post(self, request):
        """
        Handles POST requests to create a new Reservation object.
        For students and specialists.
        Accept parameters:
        - identity: "student" or "specialist" (mandatory)
        - id: student_id or specialist_id (mandatory)
        - action: "create" or "cancel" for students, "confirm" or "cancel" for specialists (mandatory)
        - reservation_id: reservation_id (optional, when identity is "specialist")
        - manager: manager_id (optional, when identity is "student" and action is "create", to be specified by the frontend, not the student.)
        - house_id: house_id (optional, when identity is "student" and action is "create")
        - period_from: begin_date (optional, when identity is "student" and action is "create")
        - period_to: end_date (optional, when identity is "student" and action is "create")
        """
        import json
        postData = json.loads(json.dumps(request.POST.dict()))
        reservation = None
        if Reservation.objects.filter(student=postData["id"]):
            reservation = Reservation.objects.filter(student=postData["id"]).latest('create_date')
        """
        if not reservation:
            return JsonResponse({"message": "Reservation not found."}, status=404)
        """
        if postData["identity"] == "student":
            if postData["action"] == "create":
                student = Student.objects.get(student_id=postData["student"])
                university_id = student.university_id
                try:
                    house = House.objects.get(id=postData["house_id"])
                    house_university = HouseUniversity.objects.get(
                        house=house,
                        university_id=university_id
                    )
                except (House.DoesNotExist, HouseUniversity.DoesNotExist):
                    return JsonResponse({
                        "message": "This accommodation is not available for your university"
                    }, status=400)
                
                try:
                    specialist = Specialist.objects.get(
                        id=postData["manager"],
                        university_id=university_id
                    )
                except Specialist.DoesNotExist:
                    return JsonResponse({
                        "message": "Specialist not found in your university"
                    }, status=400)
                
                if reservation and reservation.status != 'Cancelled':
                    return JsonResponse({"message": "You can only have one reservation at a time."}, status=400)
                if not (postData["house_id"] and postData["period_from"] and postData["period_to"]):
                    return JsonResponse({"message": "Missing required fields"}, status=400)
                postData["status"] = "Pending"
                postData["student"] = postData["id"]
                postData.pop("id")
                postData.pop("identity")
                postData.pop("action")
                serializer = self.serializer_class(data=postData, partial=True)
                if serializer.is_valid():
                    new_reservation = serializer.save()
                    try:
                        from Accommodation.services import EmailNotificationService
                        EmailNotificationService.notify_specialist_reservation_created(new_reservation)
                    except Exception as e:
                        print(f"Error sending notification email: {str(e)}")
                    
                    return JsonResponse(serializer.data, status=201)
                return JsonResponse(serializer.errors, status=400)

            elif postData["action"] == "cancel":
                if not reservation:
                    return JsonResponse({"message": "Reservation not found."}, status=404)
                if reservation.status == "Confirmed":
                    return JsonResponse({"message": "Reservation is confirmed. Therefore you can't delete it."}, status=400)
                if reservation.status == 'Cancelled':
                    return JsonResponse({"message": "Reservation is already cancelled."}, status=400)
                reservation.status = 'Cancelled'
                reservation.save()
                try:
                    from Accommodation.services import EmailNotificationService
                    EmailNotificationService.notify_specialist_reservation_cancelled(reservation)
                except Exception as e:
                    print(f"Error sending cancellation email: {str(e)}")
                return JsonResponse({"message": "Reservation cancelled"}, status=200)
            else:
                return JsonResponse({"message": "Invalid action"}, status=400)


        elif postData["identity"] == "specialist":
            reservation = Reservation.objects.get(id=postData["reservation_id"]) # reservation_id is the pk, therefore the latest() method is unnecessary.
            if not reservation:
                return JsonResponse({"message": "Reservation not found."}, status=404)
            if reservation.manager.id != int(postData["id"]):
                return JsonResponse({"message": "Only the assigned specialist can modify this reservation."}, status=400)
            if reservation.status == 'Cancelled':
                return JsonResponse({"message": "The reservation is already cancelled. You cannot modify it anymore."}, status=400)

            if postData["action"] == "cancel":
                if reservation.status == "Confirmed":
                    return JsonResponse({"message": "Reservation is confirmed. Therefore you can't delete it."}, status=400)
                if reservation.status == 'Cancelled':
                    return JsonResponse({"message": "Reservation is already cancelled."}, status=400)
                reservation.status = 'Cancelled'
                reservation.save()
                try:
                    from Accommodation.services import EmailNotificationService
                    EmailNotificationService.notify_student_reservation_cancelled(reservation)
                except Exception as e:
                    print(f"Error sending cancellation email to student: {str(e)}")
                return JsonResponse({"message": "Reservation cancelled"}, status=200)
                
            elif postData["action"] == "confirm":
                if reservation.status == "Pending":
                    reservation.status = "Confirmed"
                    reservation.save()
                    try:
                        from Accommodation.services import EmailNotificationService
                        EmailNotificationService.notify_student_reservation_confirmed(reservation)
                    except Exception as e:
                        print(f"Error sending confirmation email to student: {str(e)}")
                    return JsonResponse({"message": "Reservation confirmed"}, status=200)
                else:
                    return JsonResponse({"message": "Reservation is not available. It's already confirmed or has been cancelled."}, status=400)
        else:
            return JsonResponse({"message": "Invalid identity", "identity": postData["identity"], "original post": request.data}, status=400)
    
    def put(self, request):
        """        
        Accept parameters:
        - student: student_id
        - manager: manager_id (to be specified by the frontend, not the student.)
        - house_id: house_id
        - period_from: start date of the reservation
        - period_to: end date of the reservation
        """
        postData = request.data   
        try:
            reservation = None
            if postData["student"] and Reservation.objects.all().filter(student=postData["student"]):
                reservation = Reservation.objects.all().filter(student=postData["student"]).latest('create_date')
            
            if reservation and reservation.status != 'Cancelled':
                return JsonResponse({"message": "You can only have one reservation at a time."}, status=400)
            if not (postData["house_id"] and postData["period_from"] and postData["period_to"]):
                return JsonResponse({"message": "Missing required fields"}, status=400)

            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid():
                new_reservation = serializer.save()
                try:
                    from Accommodation.services import EmailNotificationService
                    EmailNotificationService.notify_specialist_reservation_created(new_reservation)
                except Exception as e:
                    print(f"Error sending notification email: {str(e)}")        
                return JsonResponse(serializer.data, status=201)
        except:
            return JsonResponse({"message": "Missing essential fields."}, status=400)

class HouseUniversityView(GenericAPIView):
    serializer_class = HouseUniversitySerializer
    
    def get(self, request):
        """
        List all house-university associations.
        """
        house_id = request.GET.get('house_id')
        university_id = request.GET.get('university_id')
        
        queryset = HouseUniversity.objects.all()
        
        if house_id:
            queryset = queryset.filter(house_id=house_id)
            
        if university_id:
            queryset = queryset.filter(university_id=university_id)
            
        serializer = self.serializer_class(queryset, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    
    def post(self, request):
        """
        Associate a house with a university.
        If university is not provided, uses the current token's university.
        """
        #data = request.data
        #print("Request data:", request.data)
        #print("Request content type:", request.content_type)
    
        house_id = request.POST.get('house_id')
        university_id = request.POST.get('university_id')
        # print(house_id,university_id) 
        
        if not university_id:
            university_id = getattr(request, 'university_id', None)
            if not university_id:
                return JsonResponse({"message": "No university specified or associated with token"}, status=400)
        
        if not house_id:
            return JsonResponse({"message": "House ID is required"}, status=400)
            
        serializer_data = {'house': house_id, 'university': university_id}
        
        serializer = self.serializer_class(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    def delete(self, request):
        """
        Remove association between a house and a university.
        """
        print("Delete request data:", request.data)
        house_id = request.data.get('house')
        university_id = getattr(request, 'university_id', None)
        print(house_id,university_id)
        if not house_id or not university_id:
            return JsonResponse({"message": "Both house and university are required"}, status=400)
        
        try:
            relation = HouseUniversity.objects.get(
                house_id=house_id,
                university_id=university_id
            )
            relation.delete()
            return JsonResponse({"message": "Association removed"}, status=200)
        except HouseUniversity.DoesNotExist:
            return JsonResponse({"message": "Association not found"}, status=404)

class RatingView(GenericAPIView):
    serializer_class = RatingSerializer
    
    def get(self, request):
        """
        Get a list of ratings for a house
        
        Required parameters:
        - house_id: House ID
        """
        house_id = request.GET.get('house_id')
        
        if not house_id:
            return JsonResponse({"message": "House ID is required"}, status=400)
            
        try:
            house = House.objects.get(id=house_id)
            university_id = getattr(request, 'university_id', None)
            if university_id and not HouseUniversity.objects.filter(
                house=house,
                university_id=university_id
            ).exists():
                return JsonResponse({"message": "This house is not available to your university"}, status=403)
                
            ratings = Rating.objects.filter(house=house)
            
            serializer = self.serializer_class(ratings, many=True)
            return JsonResponse(serializer.data, safe=False, status=200)
            
        except House.DoesNotExist:
            return JsonResponse({"message": "House not found"}, status=404)
    
    def post(self, request):
        """
        Add a rating for a house
        
        Required parameters:
        - house_id: House ID
        - student_id: Student ID
        - score: Rating (0.0-5.0)
        - comment: Review text
        """
        import json
        postData = json.loads(json.dumps(request.POST.dict()))
        
        house_id = postData.get('house_id')
        student_id = postData.get('student_id')
        score = postData.get('score')
        comment = postData.get('comment')
        
        if not all([house_id, student_id, score, comment]):
            return JsonResponse({"message": "All fields are required"}, status=400)
            
        try:
            house = House.objects.get(id=house_id)
            student = Student.objects.get(student_id=student_id)
            
            if not HouseUniversity.objects.filter(
                house=house,
                university_id=student.university_id
            ).exists():
                return JsonResponse({"message": "This house is not available to your university"}, status=403)
            
            reservations = Reservation.objects.filter(
                student=student,
                house_id=house,
                status='Confirmed',
                period_to__lt=datetime.now().date()
            )
            
            if not reservations.exists():
                return JsonResponse({"message": "Only students with completed contracts can rate houses"}, status=400)
            
            if Rating.objects.filter(house=house, student=student).exists():
                return JsonResponse({"message": "You have already rated this house"}, status=400)
                
            rating = Rating.objects.create(
                house=house,
                student=student,
                score=float(score),
                comment=comment
            )
            
            serializer = self.serializer_class(rating)
            return JsonResponse(serializer.data, status=201)
            
        except House.DoesNotExist:
            return JsonResponse({"message": "House not found"}, status=404)
        except Student.DoesNotExist:
            return JsonResponse({"message": "Student not found"}, status=404)
        except ValueError:
            return JsonResponse({"message": "Score must be a valid number"}, status=400)