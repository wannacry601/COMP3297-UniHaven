from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import GenericAPIView
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
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=401)
    return JsonResponse({"message": "Method not allowed"}, status=405)
    
class HouseListView(GenericAPIView):
    serializer_class = HouseSerializer
    
    @override
    def get_queryset(self, filter_by=None, order_by=None):
        """
        Returns a queryset of House objects.
        Filters and sorts the queryset based on the provided parameters.
        If no parameters are provided, returns all House objects.
        """
        queryset = House.objects.all()
        filter = self.request.query_params.get(filter_by)
        sort = self.request.query_params.get(order_by)
        if filter and sort:
            queryset = queryset.filter(name__contains=filter).order_by(sort)
        elif filter:
            queryset = queryset.filter(name__contains=filter)
        elif sort:
            queryset = queryset.order_by(sort)
        else:
            queryset = House.objects.all()
            
        return queryset

    @login_required
    def get(self,request,filter_by,order_by):
        """
        Handles GET requests to retrieve House objects.
        """
        queryset = self.get_queryset(filter_by, order_by)
        serializer = self.serializer_class(queryset, many=True)
        return JsonResponse(serializer.data)

    @permission_required('Accommodation.add_house', raise_exception=True)
    def post(self,request):
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
    
    @override
    def get_queryset(self, house_id):
        """
        Returns a queryset of House objects filtered by house_id.
        """
        return House.objects.filter(id=house_id)

    @login_required
    def get(self,request,house_id):
        """
        Handles GET requests to retrieve a specific House object by house_id.
        """
        queryset = self.get_queryset(house_id)
        serializer = self.serializer_class(queryset, many=True)
        return JsonResponse(serializer.data)

    @permission_required('Accommodation.change_house', raise_exception=True)
    def post(self,request,house_id):
        """
        Handles POST requests to update a specific House object by house_id.
        """
        queryset = self.get_queryset(house_id)
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
