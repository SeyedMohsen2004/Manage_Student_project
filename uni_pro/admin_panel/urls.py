from django.urls import path
from .views import *

urlpatterns = [
    path('register/', AdminRegisterView.as_view(), name='admin-register'),
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('foods/', FoodCreateListView.as_view(), name='admin-food-list-create'),
    path('foods/<int:pk>/', FoodDetailView.as_view(), name='admin-food-detail'),
    path('courses/', CourseCreateListView.as_view(), name='admin-course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='admin-course-detail'),
    path('students/', StudentListForAdminView.as_view(), name='admin-student-list'),
    path('students/<int:pk>/', StudentDetailForAdminView.as_view(), name='admin-student-detail'),
    path('reservations/', AllReservationsView.as_view(), name='admin-all-reservations'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
]
