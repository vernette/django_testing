from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from news.models import Comment, News

NEWS_TITLE: str = 'Заголовок новости'
NEWS_TEXT: str = 'Текст новости'
COMMENT_TEXT: str = 'Текст комментария'
NEW_COMMENT_TEXT: str = 'Обновлённый текст комментария'
NEWS_AUTHOR_TEXT: str = 'Автор'
NEWS_DEFAULT_USER_TEXT: str = 'Пользователь'
NEW_NEWS_TEXT: str = 'Обновлённый текст заметки'
NEW_NEWS_TITLE: str = 'Обновлённый заголовок заметки'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username=NEWS_AUTHOR_TEXT)


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username=NEWS_DEFAULT_USER_TEXT)


@pytest.fixture
def user_client(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title=NEWS_TITLE,
        text=NEWS_TEXT,
    )


@pytest.fixture
def news_list():
    return News.objects.bulk_create(
        News(
            title=f'{NEWS_TITLE} {i}',
            text=f'{NEWS_TEXT} {i}',
            date=timezone.now() - timezone.timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news_with_comments(news, author, comment):
    return (
        news,
        [
            Comment.objects.create(
                news=news,
                author=author,
                text=f'{COMMENT_TEXT} {index}',
                created=timezone.now() + timedelta(days=index)
            )
            for index in range(2)
        ]
    )


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def comment_form_data():
    return {
        'text': NEW_COMMENT_TEXT,
    }
