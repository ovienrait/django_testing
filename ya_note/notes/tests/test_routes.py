from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступности главной страницы, а также страниц
        регистрации, логина и логаута для неавторизованного пользователя
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authorized_user(self):
        """Проверка доступности страниц для авторизованного пользователя"""
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_delete(self):
        """Проверка доступности страниц для автора заметок и
        другого пользователя
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        names = ('notes:edit', 'notes:detail', 'notes:delete')
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in names:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка переадресации страниц"""
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
