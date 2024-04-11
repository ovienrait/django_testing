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

    def test_pages_availability(self):
        """Проверка доступности страниц"""
        urls_and_users_statuses = (
            ('notes:home', None, None, HTTPStatus.OK),
            ('notes:home', None, self.author, HTTPStatus.OK),
            ('users:login', None, None, HTTPStatus.OK),
            ('users:logout', None, self.author, HTTPStatus.OK),
            ('users:signup', None, None, HTTPStatus.OK),
            ('notes:add', None, self.author, HTTPStatus.OK),
            ('notes:list', None, self.author, HTTPStatus.OK),
            ('notes:success', None, self.author, HTTPStatus.OK),
            ('notes:edit', (self.note.slug,), self.author, HTTPStatus.OK),
            (
                'notes:edit',
                (self.note.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            ('notes:detail', (self.note.slug,), self.author, HTTPStatus.OK),
            (
                'notes:detail',
                (self.note.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
            ('notes:delete', (self.note.slug,), self.author, HTTPStatus.OK),
            (
                'notes:delete',
                (self.note.slug,),
                self.reader,
                HTTPStatus.NOT_FOUND
            ),
        )
        for name, args, user, expected_status in urls_and_users_statuses:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                if user is None:
                    response = self.client.get(url)
                else:
                    self.client.force_login(user)
                    response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

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
