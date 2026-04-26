from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group
from users.models import User
from lms.models import Course, Lesson, Subscription


class LessonTests(APITestCase):
    """
    Тесты для CRUD операций с уроками
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаём группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')

        # Создаём пользователей
        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='testpass123'
        )

        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            username='moderator',
            password='testpass123'
        )
        self.moderator.groups.add(self.moderator_group)

        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='testpass123'
        )

        # Создаём курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.owner
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner
        )

    def test_create_lesson_success(self):
        """Тест успешного создания урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_invalid_youtube_link(self):
        """Тест создания урока с недопустимой ссылкой (не youtube)"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://rutube.ru/video/test',
            'course': self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_create_lesson_moderator_forbidden(self):
        """Тест: модератор не может создавать уроки"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-list-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_lessons_list(self):
        """Тест получения списка уроков"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Title')

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_update_lesson_other_user_forbidden(self):
        """
        Тест: другой пользователь не может обновить чужой урок
        (получает 404, так как не видит чужой объект из-за фильтрации в get_queryset)
        """
        self.client.force_authenticate(user=self.other_user)
        url = reverse('lesson-detail', args=[self.lesson.id])
        data = {'title': 'Hacked Title'}
        response = self.client.patch(url, data)
        # Другой пользователь не видит чужой урок, поэтому получает 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator_forbidden(self):
        """Тест: модератор не может удалять уроки"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(APITestCase):
    """
    Тесты для подписки на обновления курса
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

    def test_create_subscription(self):
        """Тест создания подписки"""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['subscribed'])
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_delete_subscription(self):
        """Тест удаления подписки"""
        # Сначала создаём подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['subscribed'])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_missing_course_id(self):
        """Тест: отсутствует ID курса"""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        data = {}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_subscription_invalid_course_id(self):
        """Тест: неверный ID курса"""
        self.client.force_authenticate(user=self.user)
        url = reverse('subscription')
        data = {'course_id': 999}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_unauthenticated(self):
        """Тест: неавторизованный пользователь не может подписаться"""
        url = reverse('subscription')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_is_subscribed_field(self):
        """Тест: поле is_subscribed в сериализаторе курса"""
        # Создаём подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])


class CourseTests(APITestCase):
    """
    Тесты для CRUD операций с курсами
    """

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')

        self.owner = User.objects.create_user(
            email='owner@example.com',
            username='owner',
            password='testpass123'
        )

        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            username='moderator',
            password='testpass123'
        )
        self.moderator.groups.add(self.moderator_group)

        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.owner
        )

    def test_create_course_success(self):
        """PASS: Владелец создаёт курс"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_create_course_moderator_forbidden(self):
        """FORBIDDEN: Модератор не может создавать курсы"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_course_unauthenticated(self):
        """UNAUTHORIZED: Неавторизованный не может создать курс"""
        url = reverse('course-list')
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_courses_list(self):
        """PASS: Получение списка курсов"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_courses_list_unauthenticated(self):
        """UNAUTHORIZED: Неавторизованный не получает список курсов"""
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_course_detail(self):
        """PASS: Получение деталей курса"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')

    def test_update_course_owner(self):
        """PASS: Владелец обновляет курс"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('course-detail', args=[self.course.id])
        data = {'title': 'Updated Course'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')

    def test_update_course_moderator(self):
        """PASS: Модератор обновляет чужой курс"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('course-detail', args=[self.course.id])
        data = {'title': 'Updated by Moderator'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated by Moderator')

    def test_update_course_other_user_forbidden(self):
        """FORBIDDEN: Другой пользователь не может обновить чужой курс"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('course-detail', args=[self.course.id])
        data = {'title': 'Hacked'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_course_owner(self):
        """PASS: Владелец удаляет курс"""
        self.client.force_authenticate(user=self.owner)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.count(), 0)

    def test_delete_course_moderator_forbidden(self):
        """FORBIDDEN: Модератор не может удалять курсы"""
        self.client.force_authenticate(user=self.moderator)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_unauthenticated(self):
        """UNAUTHORIZED: Неавторизованный не может удалить курс"""
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_detail_contains_lessons_count(self):
        """PASS: Детали курса содержат количество уроков"""
        # Создаём урок для курса
        Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner
        )

        self.client.force_authenticate(user=self.owner)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lessons_count', response.data)
        self.assertEqual(response.data['lessons_count'], 1)

    def test_course_detail_contains_lessons_list(self):
        """PASS: Детали курса содержат список уроков"""
        # Создаём урок для курса
        Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.owner
        )

        self.client.force_authenticate(user=self.owner)
        url = reverse('course-detail', args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lessons', response.data)
        self.assertEqual(len(response.data['lessons']), 1)
