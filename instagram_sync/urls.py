from django.urls import path
from .views import SyncView, PostListView, CommentCreateView

urlpatterns = [
    path("sync/", SyncView.as_view(), name="sync-posts"),
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:id>/comment/", CommentCreateView.as_view(), name="post-comment"),
]
