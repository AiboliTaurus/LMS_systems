from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели урока
    """
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_link', 'course', 'course_title']


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели курса с выводом количества уроков
    и списка всех уроков
    """
    # Задание 1: Используем SerializerMethodField для количества уроков
    lessons_count = serializers.SerializerMethodField()

    # Задание 3: Вложенный сериализатор для вывода всех уроков
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        """Метод для получения количества уроков в курсе"""
        return obj.lessons.count()
