from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import GenericAPIView
from django.shortcuts import render
from django.db.models import Q
from typing import override

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
    def get_queryset(self):
        """
        Returns a queryset of House objects.
        Filters and sorts the queryset based on the provided parameters.
        """
        queryset = House.objects.all()
        
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
            
        if filter_available_from:
            queryset = queryset.filter(available_from__lte=filter_available_from)
            
        if filter_available_to:
            queryset = queryset.filter(available_to__gte=filter_available_to)

        if sort:
            queryset = queryset.order_by(sort)
            
        return queryset

    def get(self, request):
        """
        Handles GET requests to retrieve House objects and render the list template.
        If 'format=json' is specified, returns JSON data instead.
        """
        if request.GET.get('format') == 'json':
            queryset = self.get_queryset()
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
    def get_queryset(self,house_id):
        """
        Returns a queryset of House objects filtered by house_id.
        """
        return House.objects.filter(id=house_id)

    def get(self,request,house_id):
        """
        Handles GET requests to retrieve a specific House object by house_id.
        """
        try:
            house=House.objects.get(id=house_id)
            context = {
                'house': house,
            }
            #if request.GET.get('format') == 'json':
            queryset=self.get_queryset(house_id)
            serializer = self.serializer_class(queryset, many=True)
            return JsonResponse(serializer.data,safe=False,status=200)
            #else:
            #    return render(request, self.template_name, context)
        except House.DoesNotExist:
            return JsonResponse({"message": "House not found", "house id": house_id}, status=404)

    def post(self,request,house_id):
        """
        Handles POST requests to update a specific House object by house_id.
        """
        try:
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
        queryset = Reservation.objects.all()
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
            return JsonResponse({"message": "Reservation list not found", "data": request.data}, status=404)
        
    def post(self, request):
        """
        Handles POST requests to create a new Reservation object.
        For students and specialists.
        Accept parameters:
        - identity: "student" or "specialist" (mandatory)
        - id: student_id or specialist_id (mandatory)
        - action: "create" or "cancel" for students, "confirm" or "cancel" for specialists (mandatory)

        """
        import json
        postData = json.loads(json.dumps(request.POST.dict()))
        reservation = None
        if Reservation.objects.filter(student=postData["id"]):
            reservation = Reservation.objects.filter(student=postData["id"]).latest('create_date')
            
        if postData["identity"] == "student":
            if postData["action"] == "create":
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
            
            # Check if the student has a confirmed reservation for this house that has ended
            reservations = Reservation.objects.filter(
                student=student,
                house_id=house,
                status='Confirmed',
                period_to__lt=datetime.now().date()
            )
            
            if not reservations.exists():
                return JsonResponse({"message": "Only students with completed contracts can rate houses"}, status=400)
            
            # Check if the student has already rated this house
            if Rating.objects.filter(house=house, student=student).exists():
                return JsonResponse({"message": "You have already rated this house"}, status=400)
                
            # Create rating
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