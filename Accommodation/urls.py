from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('list/', views.HouseListView.as_view()),
    path('house/<int:house_id>/', views.HouseView.as_view(),name="property_detail"),
    path('reservation/', views.ReservationView.as_view(), name="reservation"),
    path('ratings/', views.RatingView.as_view(), name="ratings"),
    path('student/', views.StudentView.as_view(), name="student"),
]