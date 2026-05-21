from rest_framework import serializers
from .models import Course, Lesson
from .validators import YouTubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели урока с валидацией ссылки на видео
    """
    course_title = serializers.CharField(source='course.title', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_link', 'course', 'course_title', 'owner',
                  'owner_email']
        read_only_fields = ['owner', 'owner_email']
        extra_kwargs = {
            'video_link': {
                'validators': [YouTubeLinkValidator()]
            }
        }


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели курса с выводом количества уроков
    и списка всех уроков
    """
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'owner', 'owner_email',
                  'is_subscribed']
        read_only_fields = ['owner', 'owner_email']

    def get_lessons_count(self, obj):
        """Метод для получения количества уроков в курсе"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Метод для проверки, подписан ли текущий пользователь на курс
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False
