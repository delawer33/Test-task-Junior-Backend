from django.db import models


class Post(models.Model):
    """
    Модель для хранения постов из Instagram
    """

    ig_id = models.CharField(
        max_length=255, unique=True, help_text="ID медиа-объекта в Instagram"
    )
    caption = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=50, blank=True, null=True)
    media_url = models.TextField(blank=True, null=True)
    permalink = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(
        help_text="Оригинальное время создания в Instagram"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Post {self.ig_id}"


class Comment(models.Model):
    """
    Модель для хранения комментариев к постам Instagram
    """

    ig_id = models.CharField(
        max_length=255, unique=True, help_text="ID комментария в Instagram"
    )
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Comment {self.ig_id}"
