from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', StudentRegisterView.as_view(), name='student-register'),
    path('login/', StudentLoginView.as_view(), name='student-login'),
    path('me/', MeView.as_view(), name='student-me'),
    path('profile/update/', ProfileUpdateView.as_view(), name='student-profile-update'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='student-change-password'),
    path('deposit/', DepositView.as_view(), name='student-deposit'),
    path('food/reserve/<int:food_id>/', ReserveFoodView.as_view(), name='student-reserve-food'),
    path('food/cancel/<int:reservation_id>/', CancelFoodReservationView.as_view(), name='student-cancel-food'),
    path('course/reserve/<int:course_id>/', ReserveCourseView.as_view(), name='student-reserve-course'),
    path('course/cancel/<int:reservation_id>/', CancelCourseReservationView.as_view(), name='student-cancel-course'),
    path('dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('foods/', AllFoodsView.as_view(), name='all-foods'),
    path('courses/', AllCoursesView.as_view(), name='all-courses'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
