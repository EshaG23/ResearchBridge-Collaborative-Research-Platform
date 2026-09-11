def notification_count(request):
    if request.user.is_authenticated:
        return {'notification_unread_count':request.user.notifications.filter(read_at__isnull=True).count()}
    return {}

