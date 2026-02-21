import requests
from django.conf import settings
from typing import Dict, List, Optional, Any


class InstagramClient:
    """
    Клиент для взаимодействия с Instagram Graph API.
    """

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.base_url = settings.INSTAGRAM_API_BASE_URL
        # Используем прокси, если они настроены в settings
        self.proxies = getattr(settings, "PROXIES", None)

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_user_media(self) -> List[Dict[str, Any]]:
        """
        Получает все медиа-объекты пользователя, обрабатывая пагинацию.
        """
        url = f"{self.base_url}/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp",
            "access_token": self.access_token,
        }

        all_media = []
        next_url = url

        while next_url:
            response = requests.get(
                next_url,
                params=params if next_url == url else None,
                proxies=self.proxies,
            )
            response.raise_for_status()
            data = response.json()

            all_media.extend(data.get("data", []))
            next_url = data.get("paging", {}).get("next")

        return all_media

    def create_comment(self, media_id: str, text: str) -> Dict[str, Any]:
        """
        Создает комментарий к медиа-объекту в Instagram.
        """
        url = f"{self.base_url}/{media_id}/comments"
        payload = {"message": text, "access_token": self.access_token}

        response = requests.post(url, data=payload, proxies=self.proxies)
        response.raise_for_status()
        return response.json()

    def get_media_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о конкретном медиа-объекте для проверки его существования.
        """
        url = f"{self.base_url}/{media_id}"
        params = {"fields": "id", "access_token": self.access_token}

        response = requests.get(url, params=params, proxies=self.proxies)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
