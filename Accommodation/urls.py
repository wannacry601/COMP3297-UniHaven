from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),
    path('login/', views.login),
    path('list/', views.HouseListView.as_view()),
    path('house/<int:house_id>/', views.HouseView.as_view(),name="property_detail"),
    path('reservation/', views.ReservationView.as_view(), name="reservation"),
]