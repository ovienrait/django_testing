import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('id_for_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
def test_pages_avaliability(client, name, args):
    """Проверка доступности страниц анонимному пользователю"""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment'))
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, args
):
    """Проверка доступности страниц удаления и редактирования комментария"""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_comment')),
        ('news:delete', pytest.lazy_fixture('id_for_comment'))
    ),
)
@pytest.mark.django_db
def test_redirect_for_anonymous(client, name, args):
    """Проверка перенаправления неавторизованного пользователя на страницу
    авторизации при попытке редактирования или удаления комментария
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
