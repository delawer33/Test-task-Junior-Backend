from typing import List, Dict, Any
from django.utils.dateparse import parse_datetime
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
        Получает все медиа-объекты пользователя из Instagram и сохраняет/обновляет их в БД.
        Реализует логику Upsert.
        """
        media_data = self.client.get_user_media()
        synced_posts = []

        for item in media_data:
            ig_id = item.get("id")
            defaults = {
                "caption": item.get("caption"),
                "media_type": item.get("media_type"),
                "media_url": item.get("media_url"),
                "permalink": item.get("permalink"),
                "timestamp": parse_datetime(item.get("timestamp"))
                if item.get("timestamp")
                else None,
            }

            # Обновляем существующий пост или создаем новый (логика Upsert)
            post, created = Post.objects.update_or_create(
                ig_id=ig_id, defaults=defaults
            )
            synced_posts.append(post)

        return synced_posts
