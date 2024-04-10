from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Другая заметка',
            'text': 'Текст'
        }
        cls.login_url = reverse('users:login')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

    def test_authorized_user_can_create_note(self):
        """Проверка возможности создания заметки авторизованным
        пользователем
        """
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)
        created_note = Note.objects.exclude(id=self.note.id).get()
        self.assertEqual(created_note.title, self.form_data['title'])
        self.assertEqual(created_note.text, self.form_data['text'])

    def test_anonymous_user_cant_create_note(self):
        """Проверка невозможности создания заметки неавторизованным
        пользователем
        """
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверка возможности редактирования заметки автором"""
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_user_cant_edit_note_of_another_user(self):
        """Проверка невозможности редактирования заметки другим
        пользователем
        """
        response = self.reader_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(self.note.title, note.title)
        self.assertEqual(self.note.text, note.text)

    def test_author_can_delete_note(self):
        """Проверка возможности удаления заметки автором"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверка невозможности удаления заметки другим пользователем"""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_for_unique_slug(self):
        """Проверка невозможности создания заметок с одинаковым slug"""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Проверка автоматического формирования slug"""
        response = self.author_client.post(self.add_url, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(id=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
