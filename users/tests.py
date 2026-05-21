from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class UserAPITests(APITestCase):
    """
    Тесты для API пользователей
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='testpass123'
        )

    def test_register_user_success(self):
        """PASS: Регистрация нового пользователя"""
        url = reverse('register-list')
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_register_user_password_mismatch(self):
        """ERROR: Пароли не совпадают"""
        url = reverse('register-list')
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'pass123',
            'password2': 'pass456'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_users_list_authenticated(self):
        """PASS: Авторизованный получает список пользователей"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_list_unauthenticated(self):
        """UNAUTHORIZED: Неавторизованный не получает список"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_profile(self):
        """PASS: Получение своего профиля (полная информация)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')

    def test_get_other_profile_limited(self):
        """PASS: Получение чужого профиля (ограниченная информация)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', args=[self.other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Чужой профиль НЕ должен содержать историю платежей
        self.assertNotIn('payments', response.data)

    def test_update_own_profile(self):
        """PASS: Редактирование своего профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', args=[self.user.id])
        data = {'city': 'Moscow'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, 'Moscow')

    def test_update_other_profile_forbidden(self):
        """FORBIDDEN: Редактирование чужого профиля"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-detail', args=[self.other_user.id])
        data = {'city': 'Moscow'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TokenAPITests(APITestCase):
    """
    Тесты для JWT токенов
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_token_obtain_success(self):
        """PASS: Получение токена с правильными данными"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_invalid_password(self):
        """ERROR: Неверный пароль"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """PASS: Обновление токена"""
        # Сначала получаем токен
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        refresh_token = response.data['refresh']

        # Обновляем токен
        url = reverse('token_refresh')
        data = {'refresh': refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
