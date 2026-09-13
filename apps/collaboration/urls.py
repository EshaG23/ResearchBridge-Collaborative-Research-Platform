from django.urls import path
from . import views
app_name='collaboration'
urlpatterns=[path('<uuid:pk>/chat/feed/',views.feed,name='feed'),path('<uuid:pk>/chat/send/',views.post,name='send'),path('<uuid:pk>/chat/polls/<int:poll_id>/',views.poll_action,name='poll'),path('<uuid:pk>/chat/media/',views.media,name='media'),path('<uuid:pk>/chat/files/<uuid:attachment_id>/',views.attachment,name='attachment'),path('<uuid:pk>/announcements/new/',views.announcement_edit,name='announcement-new'),path('<uuid:pk>/announcements/<int:record_id>/edit/',views.announcement_edit,name='announcement-edit'),path('<uuid:pk>/announcements/',views.announcements,name='announcements'),path('<uuid:pk>/chat/',views.chat,name='chat')]
