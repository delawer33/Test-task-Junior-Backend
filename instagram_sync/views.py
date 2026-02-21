from rest_framework import generics, status, response
from rest_framework.views import APIView
from rest_framework.pagination import CursorPagination
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from requests.exceptions import HTTPError

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, CommentCreateSerializer
from .services.sync_service import SyncService
from .services.ig_client import InstagramClient


class PostCursorPagination(CursorPagination):
    """
    Пагинация для списка постов
    """

    page_size = 10
    ordering = "-timestamp"


class SyncView(APIView):
    """
    Запуск синхронизации постов из Instagram в локальную БД
    """

    @extend_schema(responses={200: PostSerializer(many=True)})
    def post(self, request, *args, **kwargs):
        service = SyncService()
        synced_posts = service.sync_posts()
        serializer = PostSerializer(synced_posts, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class PostListView(generics.ListAPIView):
    """
    Получение списка всех сохраненных постов с пагинацией
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostCursorPagination


class CommentCreateView(APIView):
    """
    Создание комментария в Instagram и его сохранения в локальной БД
    """

    @extend_schema(request=CommentCreateSerializer, responses={201: CommentSerializer})
    def post(self, request, id, *args, **kwargs):
        # Проверяем, существует ли пост в БД
        post = get_object_or_404(Post, pk=id)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["text"]

        client = InstagramClient()

        # Проверяем существует ли пост в Instagram
        try:
            ig_post = client.get_media_info(post.ig_id)
            if not ig_post:
                return response.Response(
                    {
                        "error": "Пост найден в локальной БД, но отсутствует в Instagram."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        except HTTPError as e:
            status_code = (
                e.response.status_code if e.response else status.HTTP_400_BAD_REQUEST
            )
            return response.Response(
                {"error": f"Ошибка Instagram API при проверке поста: {str(e)}"},
                status=status_code,
            )

        # Создаем комментарий в Instagram и сохраняем в БД
        try:
            ig_comment = client.create_comment(post.ig_id, text)

            comment = Comment.objects.create(
                ig_id=ig_comment.get("id"), post=post, text=text
            )

            output_serializer = CommentSerializer(comment)
            return response.Response(
                output_serializer.data, status=status.HTTP_201_CREATED
            )

        except HTTPError as e:
            return response.Response(
                {"error": f"Ошибка Instagram API при создании комментария: {str(e)}"},
                status=e.response.status_code
                if hasattr(e.response, "status_code")
                else 400,
            )
