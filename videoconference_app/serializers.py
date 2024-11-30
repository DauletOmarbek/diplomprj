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

#***********************************************************************************************************

from rest_framework import serializers
from .models import Test, Question, TestResult, Announcement

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'correct_answer']

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'lesson', 'title', 'created_at', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(test=test, **question_data)
        return test

class TestResultSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = ['id', 'student', 'test', 'score', 'total_questions', 'completed_at', 'percentage']

    def get_percentage(self, obj):
        return obj.percentage()

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'lesson', 'title', 'description', 'scheduled_date', 'created_at']