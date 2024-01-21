from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст комментария'
EXPECTED_OPERATION_SUCCESS = 1
EXPECTED_OPERATION_FAILURE = 0


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    client.post(reverse('news:detail', args=[news.id]), data=comment_form_data)
    comment_count = Comment.objects.count()
    assert comment_count == EXPECTED_OPERATION_FAILURE


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news, comment_form_data):
    url = reverse('news:detail', args=[news.id])
    author_client.post(url, data=comment_form_data)
    comment_count = Comment.objects.count()
    assert comment_count == EXPECTED_OPERATION_SUCCESS


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    form_errors = response.context['form'].errors
    assert form_errors['text'][0] == WARNING


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    url = reverse('news:delete', args=(news.id,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == EXPECTED_OPERATION_FAILURE


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client, news, comment):
    url = reverse('news:delete', args=(news.id,))
    response = client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == EXPECTED_OPERATION_SUCCESS


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        news,
        comment,
        comment_form_data
):
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.get().text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        user_client,
        news,
        comment,
        comment_form_data
):
    url = reverse('news:edit', args=(news.id,))
    response = user_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.get().text == COMMENT_TEXT
