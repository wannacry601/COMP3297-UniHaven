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
                
        if filter_location:
            queryset = queryset.filter(location__in=filter_location)
            
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
            print(1)
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

    def post(self, request):
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
            return JsonResponse({"message": "House not found"}, status=404)

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
        For students only.
        Accept parameters:
        - id: student_id
        """
        student_id = request.data["id"]
        queryset = self.get_queryset(student=student_id)
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
        if postData["identity"] == "student":
            if postData["action"] == "create":
                if not (postData["house_id"] and postData["period_from"] and postData["period_to"]):
                    return JsonResponse({"message": "Missing required fields"}, status=400)
                postData["status"] = "Pending"
                postData["student"] = postData["id"]
                postData.pop("id")
                postData.pop("identity")
                postData.pop("action")
                serializer = self.serializer_class(data=postData, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=201)
                return JsonResponse(serializer.errors, status=400)
            elif postData["action"] == "cancel":
                reservation = Reservation.objects.get(student=postData["id"])
                if reservation:
                    if reservation.status == "Confirmed":
                        return JsonResponse({"message": "Reservation is confirmed. Therefore you can't delete it."}, status=400)
                    reservation.delete()
                    return JsonResponse({"message": "Reservation cancelled"}, status=200)
                else:
                    return JsonResponse({"message": "Reservation not found"}, status=404)
            else:
                return JsonResponse({"message": "Invalid action"}, status=400)
            
        elif postData["identity"] == "specialist":
            reservation = Reservation.objects.get(id=postData["reservation_id"])
            if not reservation:
                return JsonResponse({"message": "Reservation not found."}, status=404)
            if reservation.manager != postData["id"]:
                return JsonResponse({"message": "Only the assigned specialist can modify this reservation."}, status=400)

            if postData["action"] == "cancel":
                if reservation.status == "Confirmed":
                    return JsonResponse({"message": "Reservation is confirmed. Therefore you can't delete it."}, status=400)
                reservation.delete()
                return JsonResponse({"message": "Reservation cancelled"}, status=200)
                
            elif postData["action"] == "confirm":
                if reservation.status == "Pending":
                    reservation.status = "Confirmed"
                    reservation.save()
                else:
                    return JsonResponse({"message": "Reservation is already confirmed"}, status=400)
                return JsonResponse({"message": "Reservation confirmed"}, status=200)
        
        else:
            return JsonResponse({"message": "Invalid identity", "identity": postData["identity"], "original post": request.data}, status=400)