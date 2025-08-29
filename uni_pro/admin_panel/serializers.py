from rest_framework import serializers
from .models import Food, Course
from students.models import FoodReservation, CourseReservation, User
from django.contrib.auth.password_validation import validate_password

class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role')
        extra_kwargs = {'role': {'read_only': True}}

    def create(self, validated_data):
        validated_data['role'] = 'admin'  
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class FoodReservationAdminSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    food = serializers.StringRelatedField()

    class Meta:
        model = FoodReservation
        fields = ('id','student','food','price_paid','created_at')

class CourseReservationAdminSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = CourseReservation
        fields = ('id','student','course','price_paid','created_at')

class StudentForAdminSerializer(serializers.ModelSerializer):
    food_reservations = FoodReservationAdminSerializer(many=True, read_only=True)
    course_reservations = CourseReservationAdminSerializer(many=True, read_only=True)
    profile_image = serializers.ImageField(read_only=True)
    class Meta:
        model = User
        fields = ('id','username','email','amount','role','profile_image','food_reservations','course_reservations')
