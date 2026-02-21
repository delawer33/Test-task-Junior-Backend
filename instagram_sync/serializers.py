from rest_framework import serializers
from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "ig_id",
            "caption",
            "media_type",
            "media_url",
            "permalink",
            "timestamp",
            "comment_count",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "ig_id", "post", "text", "timestamp"]


class CommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, max_length=1000)
