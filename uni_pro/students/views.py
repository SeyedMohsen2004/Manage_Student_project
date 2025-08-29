from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from decimal import Decimal

from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, FoodReservation, CourseReservation
from admin_panel.models import Food, Course
from .serializers import (
    UserRegisterSerializer, DepositSerializer,
    FoodReservationDetailSerializer, CourseReservationDetailSerializer,
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
)
from rest_framework import generics, permissions
from admin_panel.models import Food, Course
from .serializers import FoodSerializer, CourseSerializer
from rest_framework.parsers import MultiPartParser, FormParser
class StudentRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)

        # 👇 دوباره serialize برای گرفتن URL عکس
        serializer = UserRegisterSerializer(user, context={'request': request})

        data = serializer.data
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)

        return Response(data, status=status.HTTP_201_CREATED)


# لاگین دانشجو با JWT
class StudentLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = get_object_or_404(User, username=username, role='student')
        if not user.check_password(password):
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            "id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
# مشاهده اطلاعات خود دانشجو
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

# آپدیت پروفایل
class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

# تغییر رمز
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail':'Password changed successfully'}, status=status.HTTP_200_OK)

# واریز پول
class DepositView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        user = request.user
        user.amount = F('amount') + amount
        user.save(update_fields=['amount'])
        user.refresh_from_db()
        return Response({'detail':'Deposit successful', 'new_amount': str(user.amount)}, status=status.HTTP_200_OK)

# رزرو غذا
class ReserveFoodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, food_id):
        user = request.user
        food = get_object_or_404(Food.objects.select_for_update(), pk=food_id)
        if food.capacity <= 0:
            return Response({'detail':'No capacity for this food'}, status=status.HTTP_400_BAD_REQUEST)
        if user.amount < food.price:
            return Response({'detail':'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        user.amount = F('amount') - food.price
        user.save(update_fields=['amount'])
        food.capacity = F('capacity') - 1
        food.save(update_fields=['capacity'])
        user.refresh_from_db()
        food.refresh_from_db()
        res = FoodReservation.objects.create(student=user, food=food, price_paid=food.price)
        return Response({'detail':'Reserved', 'reservation_id': res.id, 'new_amount': str(user.amount)}, status=201)

# لغو رزرو غذا
class CancelFoodReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, reservation_id):
        user = request.user
        reservation = get_object_or_404(FoodReservation.objects.select_for_update(), pk=reservation_id, student=user)
        food = get_object_or_404(Food.objects.select_for_update(), pk=reservation.food.pk)
        user.amount = F('amount') + reservation.price_paid
        user.save(update_fields=['amount'])
        food.capacity = F('capacity') + 1
        food.save(update_fields=['capacity'])
        reservation.delete()
        user.refresh_from_db()
        food.refresh_from_db()
        return Response({'detail':'Cancelled and refunded', 'new_amount': str(user.amount)}, status=200)

# رزرو دوره
class ReserveCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, course_id):
        user = request.user
        course = get_object_or_404(Course.objects.select_for_update(), pk=course_id)
        if course.capacity <= 0:
            return Response({'detail':'No capacity for this course'}, status=status.HTTP_400_BAD_REQUEST)
        if user.amount < course.cost:
            return Response({'detail':'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)
        user.amount = F('amount') - course.cost
        user.save(update_fields=['amount'])
        course.capacity = F('capacity') - 1
        course.save(update_fields=['capacity'])
        user.refresh_from_db()
        course.refresh_from_db()
        res = CourseReservation.objects.create(student=user, course=course, price_paid=course.cost)
        return Response({'detail':'Course reserved', 'reservation_id': res.id, 'new_amount': str(user.amount)}, status=201)

# لغو رزرو دوره
class CancelCourseReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, reservation_id):
        user = request.user
        reservation = get_object_or_404(CourseReservation.objects.select_for_update(), pk=reservation_id, student=user)
        course = get_object_or_404(Course.objects.select_for_update(), pk=reservation.course.pk)
        user.amount = F('amount') + reservation.price_paid
        user.save(update_fields=['amount'])
        course.capacity = F('capacity') + 1
        course.save(update_fields=['capacity'])
        reservation.delete()
        user.refresh_from_db()
        course.refresh_from_db()
        return Response({'detail':'Course reservation cancelled and refunded', 'new_amount': str(user.amount)}, status=200)

# داشبورد دانشجو
class StudentDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user, context={'request': request})
        food_res = FoodReservation.objects.filter(student=user).order_by('-created_at')
        course_res = CourseReservation.objects.filter(student=user).order_by('-created_at')
        food_serializer = FoodReservationDetailSerializer(food_res, many=True, context={'request': request})
        course_serializer = CourseReservationDetailSerializer(course_res, many=True, context={'request': request})
        return Response({
            'user': user_serializer.data,
            'food_reservations': food_serializer.data,
            'course_reservations': course_serializer.data
        })

# تمام غذاها
class AllFoodsView(generics.ListAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]

# تمام دوره‌ها
class AllCoursesView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]