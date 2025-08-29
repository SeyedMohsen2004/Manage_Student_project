from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Food, Course
from students.models import User, FoodReservation, CourseReservation
from .serializers import (
    FoodSerializer, CourseSerializer,
    StudentForAdminSerializer,
    FoodReservationAdminSerializer,
    CourseReservationAdminSerializer,
    AdminRegisterSerializer  
)

class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin')

class AdminRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)
        response.data['access'] = str(refresh.access_token)
        response.data['refresh'] = str(refresh)
        return response

class AdminLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = get_object_or_404(User, username=username, role='admin')
        if not user.check_password(password):
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            "id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

class FoodCreateListView(generics.ListCreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class FoodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class CourseCreateListView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class StudentListForAdminView(generics.ListAPIView):
    queryset = User.objects.filter(role='student').order_by('username')
    serializer_class = StudentForAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class StudentDetailForAdminView(generics.RetrieveAPIView):
    queryset = User.objects.filter(role='student')
    serializer_class = StudentForAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

class AllReservationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        food_res = FoodReservation.objects.select_related('student','food').order_by('-created_at')[:200]
        course_res = CourseReservation.objects.select_related('student','course').order_by('-created_at')[:200]
        food_ser = FoodReservationAdminSerializer(food_res, many=True)
        course_ser = CourseReservationAdminSerializer(course_res, many=True)
        return Response({'food_reservations': food_ser.data, 'course_reservations': course_ser.data})

class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        total_students = User.objects.filter(role='student').count()
        total_foods = Food.objects.count()
        total_courses = Course.objects.count()
        total_balance = User.objects.filter(role='student').aggregate(total=Sum('amount'))['total'] or 0
        total_food_res = FoodReservation.objects.count()
        total_course_res = CourseReservation.objects.count()

        return Response({
            'total_students': total_students,
            'total_foods': total_foods,
            'total_courses': total_courses,
            'total_student_balance': str(total_balance),
            'total_food_reservations': total_food_res,
            'total_course_reservations': total_course_res,
        })
