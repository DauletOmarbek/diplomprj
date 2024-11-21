#urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, CourseViewSet, EnrollmentRequestViewSet, LessonViewSet, CourseMaterialViewSet



router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'enrollment_requests', EnrollmentRequestViewSet, basename='enrollment_requests')
router.register(r'lessons', LessonViewSet, basename='lessons')
router.register(r'course_materials', CourseMaterialViewSet, basename='course_materials')



urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login_view, name='login'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('meeting/',views.videocall, name='meeting'),
    path('logout/',views.logout_view, name='logout'),
    path('join/',views.join_room, name='join_room'),
    path('',views.index, name='index'),
    path('courses/', views.course_list, name='course_list'),
    path('manage_requests/', views.manage_requests, name='manage_requests'),
    path('respond_request/<int:request_id>/<str:action>/', views.respond_request, name='respond_request'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/add_lesson/', views.add_lesson, name='add_lesson'),
    path('create_course/', views.create_course, name='create_course'),
    path('view_courses/', views.view_courses, name='view_courses'), 
    path('my_courses/', views.my_courses, name='my_courses'),
    path('add_student/<int:course_id>/', views.add_student_to_course, name='add_student_to_course'),
    path('request_enrollment/<int:course_id>/', views.request_enrollment, name='request_enrollment'),
    path('my_enrolled_courses/', views.my_enrolled_courses, name='my_enrolled_courses'),
    path('student_course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),



    path('api/', include(router.urls)),



]