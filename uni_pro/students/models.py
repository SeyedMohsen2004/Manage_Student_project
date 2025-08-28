
# app: student/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

def profile_image_upload_to(instance, filename):
    return f'profiles/{instance.username}/{filename}'

class User(AbstractUser):
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ROLE_CHOICES = (('student', 'Student'), ('admin', 'Admin'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField(upload_to=profile_image_upload_to, blank=True, null=True)  # اضافه شد

    def __str__(self):
        return f"{self.username} ({self.role})"

class FoodReservation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_reservations')
    food = models.ForeignKey('admin_panel.Food', on_delete=models.CASCADE, related_name='reservations')
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FoodRes #{self.id} {self.student.username} -> {self.food.name}"

class CourseReservation(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_reservations')
    course = models.ForeignKey('admin_panel.Course', on_delete=models.CASCADE, related_name='reservations')
    price_paid = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CourseRes #{self.id} {self.student.username} -> {self.course.name}"
