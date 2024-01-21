from datetime import timedelta

import pytest
from django.utils import timezone
from news.models import Comment, News

NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'
COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст комментария'
NEWS_AUTHOR_TEXT = 'Автор'
NEWS_DEFAULT_USER_TEXT = 'Пользователь'
NEW_NEWS_TEXT = 'Обновлённый текст заметки'
NEW_NEWS_TITLE = 'Обновлённый заголовок заметки'


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
    new_news = News.objects.create(
        title=NEWS_TITLE,
        text=NEWS_TEXT,
    )
    return new_news


@pytest.fixture
def news_with_comments(news, author, comment):
    now = timezone.now()
    comments = []
    for index in range(2):
        new_comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'{COMMENT_TEXT} {index}'
        )
        new_comment.created = now + timedelta(days=index)
        new_comment.save()
        comments.append(new_comment)
    return news, comments


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    new_comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return new_comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def comment_form_data():
    return {
        'text': NEW_COMMENT_TEXT,
    }
