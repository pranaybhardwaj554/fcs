from django.urls import path
from .import views
from .views import (
    UserPostListView,
    PostDeleteView,
    SharedByMe,
    SharedWithMe
)

urlpatterns = [
    path('dashboard/upload/', views.upload, name = 'upload'), 
    path('dashboard/share_docs/', views.share_docs, name = 'share_docs'), 
    path('dashboard/user_posts/', UserPostListView.as_view(), name='user-posts'),
     path('dashboard/shared_by_me/', SharedByMe.as_view(), name='shared'), 
     path('dashboard/shared_with_me/', SharedWithMe.as_view(), name='sharedMe'), 
     path('dashboard/<pk>/delete_posts/', PostDeleteView.as_view(), name='post-delete'),
]