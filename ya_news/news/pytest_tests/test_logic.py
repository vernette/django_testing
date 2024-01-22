from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст комментария'
EXPECTED_OPERATION_SUCCESS = 1
EXPECTED_OPERATION_FAILURE = 0

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    """Verifies that an anonymous user cannot create a comment"""
    client.post(reverse('news:detail', args=[news.id]), data=comment_form_data)
    comment_count = Comment.objects.count()
    assert comment_count == EXPECTED_OPERATION_FAILURE


def test_user_can_create_comment(author_client, news, comment_form_data):
    """Verifies that an authorized user can create a comment"""
    url = reverse('news:detail', args=[news.id])
    author_client.post(url, data=comment_form_data)
    comment_count = Comment.objects.count()
    assert comment_count == EXPECTED_OPERATION_SUCCESS


def test_user_cant_use_bad_words(author_client, news):
    """Verifies that a user cannot use bad words in a comment"""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    form_errors = response.context['form'].errors
    assert form_errors['text'][0] == WARNING


def test_author_can_delete_comment(author_client, news, comment):
    """Verifies that the author can delete their own comment"""
    url = reverse('news:delete', args=(news.id,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == EXPECTED_OPERATION_FAILURE


def test_user_cant_delete_comment_of_another_user(client, news, comment):
    """Verifies that a user cannot delete a comment authored by another user"""
    url = reverse('news:delete', args=(news.id,))
    response = client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == EXPECTED_OPERATION_SUCCESS


def test_author_can_edit_comment(
        author_client,
        news,
        comment,
        comment_form_data
):
    """Verifies that the author can edit their own comment"""
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.get().text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        user_client,
        news,
        comment,
        comment_form_data
):
    """Verifies that a user cannot edit a comment authored by another user"""
    url = reverse('news:edit', args=(news.id,))
    response = user_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.get().text == COMMENT_TEXT
