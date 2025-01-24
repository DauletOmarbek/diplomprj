#views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import CustomUser, Course, EnrollmentRequest, Lesson, CourseMaterial
from django.http import JsonResponse
from .serializers import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'login.html', {'success': "Registration successful. Please login."})
        else:
            error_message = form.errors.as_text()
            return render(request, 'register.html', {'error': error_message})

    return render(request, 'register.html')


def login_view(request):
    if request.method=="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/dashboard")
        else:
            return render(request, 'login.html', {'error': "Invalid credentials. Please try again."})

    return render(request, 'login.html')

def api_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Registration successful'}, status=201)
        return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def api_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'user': user.email})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def api_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

class GetUserByEmailView(APIView):
    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'name': request.user.first_name})

@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.first_name + " " + request.user.last_name})

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login")

@login_required
def join_room(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        return redirect("/meeting?roomID=" + roomID)
    return render(request, 'joinroom.html')


@login_required
def create_course(request):
    if request.user.role != 'teacher':
        return redirect('/dashboard')  # Только учитель может создавать курсы

    if request.method == 'POST':
        # Обработка данных формы создания курса (пример, добавить вашу логику)
        title = request.POST.get('title')
        description = request.POST.get('description')
        # Сохраните курс в базе данных
        Course.objects.create(
            teacher=request.user,
            title=title,
            description=description
        )
        return redirect('/dashboard')  # Перенаправление после успешного создания

    return render(request, 'create_course.html')


def course_list(request):
    courses = Course.objects.all()

    # Фильтрация по названию или описанию
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    return render(request, 'courses.html', {'courses': courses})



@login_required
def manage_requests(request):
    if request.user.role != 'teacher':
        return redirect('/dashboard')

    requests = EnrollmentRequest.objects.filter(course__teacher=request.user)
    return render(request, 'manage_requests.html', {'requests': requests})

@login_required
def respond_request(request, request_id, action):
    if request.user.role != 'teacher':
        return redirect('/dashboard')

    enrollment_request = EnrollmentRequest.objects.get(id=request_id, course__teacher=request.user)

    if action == 'accept':
        enrollment_request.status = 'accepted'
        enrollment_request.course.students.add(enrollment_request.student)
    elif action == 'reject':
        enrollment_request.status = 'rejected'

    enrollment_request.save()
    enrollment_request.delete()
    return redirect('manage_requests')



@login_required
def course_detail(request, course_id):
    # Получаем курс, созданный текущим учителем
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    students = course.students.all()  # Список студентов, записанных на курс
    return render(request, 'course_detail.html', {'course': course, 'students': students})

@login_required
def view_courses(request):
    # Логика для отображения списка курсов
    # Например, получаем все доступные курсы:
    courses = Course.objects.all()  # Предположим, что модель Course уже создана
    return render(request, 'view_courses.html', {'courses': courses})

@login_required
def my_courses(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')  # Только учитель имеет доступ

    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'my_courses.html', {'courses': courses})


@login_required
def add_student_to_course(request, course_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            student = CustomUser.objects.get(email=email, role='student')
            course.students.add(student)
            course.save()
            return redirect('my_courses')
        except CustomUser.DoesNotExist:
            return render(request, 'add_student.html', {'course': course, 'error': 'Student with this email does not exist.'})

    return render(request, 'add_student.html', {'course': course})



@login_required
def request_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # Проверяем, есть ли уже запрос или доступ
    if EnrollmentRequest.objects.filter(student=request.user, course=course, status='pending').exists() or course.students.filter(id=request.user.id).exists():
        return redirect('view_courses')

    # Создаем новый запрос
    EnrollmentRequest.objects.create(student=request.user, course=course, status='pending')
    return redirect('view_courses')

#@login_required
#def my_enrolled_courses(request):
 #   courses = request.user.enrolled_courses.all()  # Курсы, к которым студент имеет доступ
  #  return render(request, 'my_enrolled_courses.html', {'courses': courses})
@login_required
def my_enrolled_courses(request):
    courses = request.user.enrolled_courses.all()
    print(courses)  # Отображение QuerySet в консоли
    for course in courses:
        print(course.id, course.title)  # Проверка наличия id
    return render(request, 'my_enrolled_courses.html', {'courses': courses})


@login_required
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_url = request.POST.get('video_url')
        section = request.POST.get('section')

        # Создаем новый урок
        Lesson.objects.create(
            course=course,
            title=title,
            description=description,
            video_url=video_url,
            section=section
        )
        return redirect('course_detail', course_id=course.id)

    return render(request, 'add_lesson.html', {'course': course})


@login_required
def student_course_detail(request, course_id):
    # Проверяем, имеет ли студент доступ к курсу
    course = get_object_or_404(Course, id=course_id)
    if not course.students.filter(id=request.user.id).exists():
        return redirect('my_enrolled_courses')  # Перенаправление, если доступа нет

    lessons = course.lessons.all()  # Получаем все уроки курса
    return render(request, 'student_course_detail.html', {'course': course, 'lessons': lessons})



@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.user not in course.students.all() and request.user != course.teacher:
        return redirect('/courses')


    return render(request, 'course_detail.html', {'course': course})


#************************************************

from .serializers import (
    CustomUserSerializer, CourseSerializer,
    EnrollmentRequestSerializer, LessonSerializer,
    CourseMaterialSerializer
)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class EnrollmentRequestViewSet(viewsets.ModelViewSet):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class CourseMaterialViewSet(viewsets.ModelViewSet):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer



# views.py

from rest_framework import viewsets, permissions
from .models import Test, Question, TestResult, Announcement
from .serializers import TestSerializer, QuestionSerializer, TestResultSerializer, AnnouncementSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Класс для проверки, является ли пользователь учителем
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

# Класс для проверки, является ли пользователь студентом
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    


    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def take_test(self, request, pk=None):
        test = self.get_object()
        questions = test.questions.all()
        answers = request.data.get('answers', {})
        score = 0
        total_questions = questions.count()

        for question in questions:
            question_id = str(question.id)
            student_answer = answers.get(question_id, '').strip().lower()
            correct_answer = question.correct_answer.strip().lower()
            if student_answer == correct_answer:
                score += 1

        result = TestResult.objects.create(
            student=request.user,
            test=test,
            score=score,
            total_questions=total_questions
        )

        serializer = TestResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsStudent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Переопределяем метод create, чтобы автоматически вычислять процент
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

#***********************************************************************************************************
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Lesson, Test, Question, TestResult
from .forms import TestForm
from django.contrib.auth.decorators import login_required

# Учитель добавляет тест
@login_required
def add_test(request, lesson_id):
    if request.user.role != 'teacher':  # Только учитель может добавлять тесты
        return redirect('dashboard')

    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        test_title = request.POST.get('title')
        if test_title:
            test = Test.objects.create(lesson=lesson, title=test_title)
            return redirect('course_detail', course_id=lesson.course.id)  # Перенаправление на страницу курса

    return render(request, 'add_test.html', {'lesson': lesson})


# Студент проходит тест
@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()

    if request.method == 'POST':
        form = TestForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            total_questions = len(questions)

            # Проверяем ответы студента
            for question in questions:
                student_answer = form.cleaned_data.get(f'question_{question.id}').strip().lower()
                if student_answer == question.correct_answer.strip().lower():
                    score += 1

            # Сохраняем результат
            TestResult.objects.create(
                student=request.user,
                test=test,
                score=score,
                total_questions=total_questions
            )

            return redirect('test_result', test_id=test.id)

    else:
        form = TestForm(questions=questions)

    return render(request, 'take_test.html', {'test': test, 'form': form})


# Отображение результата теста
@login_required
def test_result(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    result = get_object_or_404(TestResult, student=request.user, test=test)

    return render(request, 'test_result.html', {'test': test, 'result': result})


@login_required
def view_test_results(request, test_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    test = get_object_or_404(Test, id=test_id)
    results = TestResult.objects.filter(test=test)
    return render(request, 'view_test_results.html', {'test': test, 'results': results})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Lesson, Announcement
from .forms import AnnouncementForm
from django.utils import timezone

@login_required
def add_announcement(request, lesson_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')

    lesson = get_object_or_404(Lesson, id=lesson_id, course__teacher=request.user)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.lesson = lesson
            announcement.save()
            return redirect('course_detail', course_id=lesson.course.id)
    else:
        form = AnnouncementForm()

    return render(request, 'add_announcement.html', {'form': form, 'lesson': lesson})


@login_required
def view_announcements(request):
    if request.user.role != 'student':
        return redirect('dashboard')

    # Получаем все курсы, на которые записан студент
    courses = request.user.enrolled_courses.all()

    # Получаем все уведомления из этих курсов
    announcements = Announcement.objects.filter(lesson__course__in=courses).order_by('scheduled_date')

    return render(request, 'view_announcements.html', {'announcements': announcements})

