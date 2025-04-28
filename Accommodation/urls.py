from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('',views.index),
    path('login/', views.login),
    path('list/', views.HouseListView.as_view()),
    path('house/<int:house_id>/', views.HouseView.as_view(),name="property_detail"),
    path('reservation/', views.ReservationView.as_view(), name="reservation"),
    path('ratings/', views.RatingView.as_view(), name="ratings"),
    path('token_auth/', obtain_auth_token, name='api_token_auth'),
    path('university_token/', views.create_university_token, name='university_token'),
    path('house_universities/', views.HouseUniversityView.as_view(), name="house_university"),
]