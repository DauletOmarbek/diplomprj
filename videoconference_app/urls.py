#urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, CourseViewSet, EnrollmentRequestViewSet, LessonViewSet, CourseMaterialViewSet, api_register ,api_login, api_logout
from .views import (
    CustomUserViewSet, CourseViewSet, EnrollmentRequestViewSet, LessonViewSet,
    CourseMaterialViewSet, TestViewSet, QuestionViewSet, TestResultViewSet, AnnouncementViewSet, GetUserByEmailView
)
from django.http import JsonResponse
from django.middleware.csrf import get_token

def csrf_token_view(request):
    return JsonResponse({'csrfToken': get_token(request)})


router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'enrollment_requests', EnrollmentRequestViewSet, basename='enrollment_requests')
router.register(r'lessons', LessonViewSet, basename='lessons')
router.register(r'course_materials', CourseMaterialViewSet, basename='course_materials')
router.register(r'tests', TestViewSet, basename='tests')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'test_results', TestResultViewSet, basename='test_results')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('meeting/', views.videocall, name='meeting'),
    path('logout/', views.logout_view, name='logout'),
    path('join/', views.join_room, name='join_room'),
    path('', views.index, name='index'),
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
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/result/', views.test_result, name='test_result'),
    path('lesson/<int:lesson_id>/add_test/', views.add_test, name='add_test'),
    path('test/<int:test_id>/results/', views.view_test_results, name='view_test_results'),
    path('lesson/<int:lesson_id>/add_announcement/', views.add_announcement, name='add_announcement'),
    path('announcements/', views.view_announcements, name='view_announcements'),
    path('api/register/', api_register, name='api_register'),
    path('api/login/', api_login, name='api_login'),
    path('api/logout/', api_logout, name='logout'),
    path('api/csrf/', csrf_token_view, name='csrf_token'),
    path('api/get-user-by-email/', GetUserByEmailView.as_view(), name='get-user-by-email'),
    path('api/', include(router.urls)),
]