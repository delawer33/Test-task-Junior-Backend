import pytest
import requests_mock
from django.urls import reverse
from rest_framework import status
from .models import Post, Comment
from django.utils import timezone


@pytest.mark.django_db
def test_create_comment_success(client, settings):
    post = Post.objects.create(
        ig_id="123", caption="Test Post", timestamp=timezone.now()
    )
    url = reverse("post-comment", kwargs={"id": post.id})
    settings.INSTAGRAM_ACCESS_TOKEN = "fake_token"

    with requests_mock.Mocker() as m:
        m.get(f"{settings.INSTAGRAM_API_BASE_URL}/123", json={"id": "123"})
        m.post(
            f"{settings.INSTAGRAM_API_BASE_URL}/123/comments",
            json={"id": "comm_456"},
        )

        response = client.post(
            url, {"text": "Great post!"}, content_type="application/json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["ig_id"] == "comm_456"
        assert response.data["text"] == "Great post!"
        assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_create_comment_post_not_found_locally(client):
    url = reverse("post-comment", kwargs={"id": 999})
    response = client.post(url, {"text": "Hello"}, content_type="application/json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_comment_post_not_on_instagram(client, settings):
    post = Post.objects.create(
        ig_id="123", caption="Gone Post", timestamp=timezone.now()
    )
    url = reverse("post-comment", kwargs={"id": post.id})

    with requests_mock.Mocker() as m:
        m.get(f"{settings.INSTAGRAM_API_BASE_URL}/123", status_code=404)

        response = client.post(url, {"text": "Hello"}, content_type="application/json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_create_comment_ig_api_error(client, settings):
    post = Post.objects.create(
        ig_id="123", caption="Error Post", timestamp=timezone.now()
    )
    url = reverse("post-comment", kwargs={"id": post.id})

    with requests_mock.Mocker() as m:
        m.get(f"{settings.INSTAGRAM_API_BASE_URL}/123", json={"id": "123"})
        m.post(f"{settings.INSTAGRAM_API_BASE_URL}/123/comments", status_code=400)

        response = client.post(url, {"text": "Hello"}, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
