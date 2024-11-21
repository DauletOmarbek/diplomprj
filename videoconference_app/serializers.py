from rest_framework import serializers
from .models import CustomUser, Course, EnrollmentRequest, Lesson, CourseMaterial

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'role']

class CourseSerializer(serializers.ModelSerializer):
    teacher = CustomUserSerializer()  # Вложенный сериализатор для учителя
    students = CustomUserSerializer(many=True)  # Вложенный сериализатор для студентов

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'students', 'created_at']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    student = CustomUserSerializer()
    course = CourseSerializer()

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'course', 'status', 'created_at']

class LessonSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url', 'section', 'course', 'created_at']

class CourseMaterialSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseMaterial
        fields = ['id', 'title', 'description', 'video', 'course', 'created_at']
