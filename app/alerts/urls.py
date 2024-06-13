from django.urls import path
from .views import UserAlertsView, UnreadUserAlertsView


urlpatterns = [
    # /api/v1/alerts
    path("", UserAlertsView.as_view(), name="user-alerts"),
    # /api/v1/alerts/status
    path("/status", UnreadUserAlertsView.as_view(), name="unread-alerts"),
]
