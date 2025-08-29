from rest_framework import serializers
from .models import User, FoodReservation, CourseReservation
from admin_panel.models import Food, Course
from django.contrib.auth.password_validation import validate_password

# برای نمایش خلاصه‌ی غذا و دوره در رزروها
class FoodNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id','name','category','price','imgoffood')

class CourseNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id','name','professor','grade','credits','cost')

# رزروها با اطلاعات مربوطه
class FoodReservationDetailSerializer(serializers.ModelSerializer):
    food = FoodNestedSerializer(read_only=True)
    class Meta:
        model = FoodReservation
        fields = ('id','food','price_paid','created_at')

class CourseReservationDetailSerializer(serializers.ModelSerializer):
    course = CourseNestedSerializer(read_only=True)
    class Meta:
        model = CourseReservation
        fields = ('id','course','price_paid','created_at')

# ثبت نام
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile_image = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = User
        fields = ('id','username','password','email','role','profile_image')
        extra_kwargs = {'role': {'required': False}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Serializer برای واریز پول
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

# نمایش اطلاعات کاربر (برای me و داشبورد)
class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(read_only=True)
    class Meta:
        model = User
        fields = ('id','username','email','amount','last_login','role','profile_image')

# آپدیت پروفایل کاربر (username, email, profile_image)
class UserUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username','email','profile_image')

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً گرفته شده است.")
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        if value and User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

# تغییر رمز (نیاز به رمز قدیم و رمز جدید)
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز قدیم اشتباه است.")
        return value

# student/serializers.py (اضافه شود)
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ('id','name','category','price','imgoffood','capacity')

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id','name','professor','grade','credits','cost','capacity')
