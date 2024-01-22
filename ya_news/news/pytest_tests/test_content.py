import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

NEWS_TITLE: str = 'Заголовок новости'
NEWS_TEXT: str = 'Текст новости'

pytestmark = pytest.mark.django_db


def test_number_of_news_on_home_page(client, news_list):
    """
    Check that the number of news articles on the home page
    matches the specified count
    """
    response = client.get(reverse('news:home'))
    assert (
        response.context['object_list'].count()
        == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
    )
)
def test_comments_order(client, news_with_comments, name, args):
    """Check the order of comments on the news detail page"""
    detail_url = reverse('news:detail', args=args)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_news_order(client, news_list):
    """Check the order of displayed news articles on the home page"""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_anonymous_client_has_no_form(client, news_id_for_args):
    """
    Check that an anonymous user does not see
    the comment form on the news detail page
    """
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(news_id_for_args, author_client):
    """
    Check that an authorized user sees
    the comment form on the news detail page
    """
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
