import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'name, args, parametrized_client, expected_status',
    (
        (
            'news:home',
            None,
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'news:home',
            None,
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:detail',
            pytest.lazy_fixture('id_for_news'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'news:detail',
            pytest.lazy_fixture('id_for_news'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:edit',
            pytest.lazy_fixture('id_for_comment'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:edit',
            pytest.lazy_fixture('id_for_comment'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'news:delete',
            pytest.lazy_fixture('id_for_comment'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'news:delete',
            pytest.lazy_fixture('id_for_comment'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'users:login',
            None,
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'users:logout',
            None,
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'users:signup',
            None,
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
    )
)
@pytest.mark.django_db
def test_pages_avaliability(name, args, parametrized_client, expected_status):
    """Проверка доступности страниц анонимному пользователю"""
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
