from typing import List
from django.utils.dateparse import parse_datetime
from django.db import transaction
from ..models import Post
from .ig_client import InstagramClient


class SyncService:
    """
    Сервис для синхронизации данных из Instagram в локальную базу данных.
    """

    def __init__(self, client: InstagramClient = None):
        self.client = client or InstagramClient()

    def sync_posts(self) -> List[Post]:
        """
        Синхронизирует посты из Instagram в локальную БД
        Bulk Upsert: массовое создание и обновление
        
        Можно добавить логику для удаления поста, если он 
        не существует в Instagram (удален)
        """

        media_data = self.client.get_user_media()

        existing_posts = Post.objects.in_bulk(field_name="ig_id")

        to_create = []
        to_update = []

        for item in media_data:
            ig_id = item.get("id")

            data = {
                "ig_id": ig_id,
                "caption": item.get("caption"),
                "media_type": item.get("media_type"),
                "media_url": item.get("media_url"),
                "permalink": item.get("permalink"),
                "timestamp": parse_datetime(item.get("timestamp"))
                if item.get("timestamp")
                else None,
            }

            if ig_id in existing_posts:
                post = existing_posts[ig_id]

                for field, value in data.items():
                    setattr(post, field, value)

                to_update.append(post)
            else:
                to_create.append(Post(**data))

        with transaction.atomic():
            if to_create:
                Post.objects.bulk_create(to_create)

            if to_update:
                Post.objects.bulk_update(
                    to_update,
                    fields=[
                        "caption",
                        "media_type",
                        "media_url",
                        "permalink",
                        "timestamp",
                    ],
                )

        return list(existing_posts.values()) + to_create
