from django.contrib import admin
from .models import (
    CustomUser, VideoCall, DashboardLog, Course, CourseMaterial, EnrollmentRequest, Lesson
)
from django.contrib.auth.admin import UserAdmin

# Настройка для модели CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'role']
    ordering = ['email']

# Настройка для модели VideoCall
class VideoCallAdmin(admin.ModelAdmin):
    list_display = ['room_id', 'user', 'created_at']
    search_fields = ['room_id', 'user__email']

# Настройка для модели DashboardLog
class DashboardLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'timestamp']
    search_fields = ['user__email', 'action']

# Настройка для модели Course
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'created_at']
    search_fields = ['title', 'teacher__email']
    list_filter = ['created_at']
    filter_horizontal = ('students',)  # Удобный интерфейс для добавления студентов

# Настройка для модели CourseMaterial
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'created_at']
    search_fields = ['title', 'course__title']
    list_filter = ['created_at']

# Настройка для модели EnrollmentRequest
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'created_at']
    search_fields = ['student__email', 'course__title', 'status']
    list_filter = ['status', 'created_at']

# Настройка для модели Lesson
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'section', 'created_at']
    search_fields = ['title', 'course__title', 'section']
    list_filter = ['created_at']

# Регистрация всех моделей
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VideoCall, VideoCallAdmin)
admin.site.register(DashboardLog, DashboardLogAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseMaterial, CourseMaterialAdmin)
admin.site.register(EnrollmentRequest, EnrollmentRequestAdmin)
admin.site.register(Lesson, LessonAdmin)

#***********************************************************************************************************
# admin.py
from django.contrib import admin
from .models import Test, Question, TestResult

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Количество пустых строк для добавления вопросов


class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'created_at']
    inlines = [QuestionInline]  # Инлайн-редактирование вопросов


class TestResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'score', 'total_questions', 'percentage', 'completed_at']

admin.site.register(Test, TestAdmin)
admin.site.register(TestResult, TestResultAdmin)


from .models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'scheduled_date', 'created_at']
    search_fields = ['title', 'lesson__title', 'description']
    list_filter = ['scheduled_date', 'created_at']

admin.site.register(Announcement, AnnouncementAdmin)
