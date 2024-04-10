from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='zametka',
            author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_note_list_for_author(self):
        """Проверка отображения заметок для автора"""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        notes = response.context['note_list']
        self.assertIn(self.note, notes)

    def test_note_list_for_reader(self):
        """Проверка отображения заметок для другого пользователя"""
        self.client.force_login(self.reader)
        response = self.client.get(self.list_url)
        notes = response.context['note_list']
        self.assertNotIn(self.note, notes)

    def test_authorized_user_has_form(self):
        """Проверка отображения формы создания и редактирования заметки
        для авторизованного пользователя
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
