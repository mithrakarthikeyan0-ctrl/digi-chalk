from django.urls import path
from . import views

urlpatterns = [
    # Parent endpoints
    path('parent/communication-preferences/', views.ParentCommunicationPreferenceView.as_view(), name='parent-communication-preferences'),
    path('parent/notifications/', views.ParentNotificationListView.as_view(), name='parent-notifications'),

    # Teacher endpoints
    path('teacher/notifications/drafts/', views.TeacherNotificationDraftView.as_view(), name='teacher-notification-drafts'),

    # Admin endpoints
    path('notifications/pending-approval/', views.AdminPendingApprovalListView.as_view(), name='admin-pending-approvals'),
    path('notifications/<uuid:pk>/<str:action>/', views.AdminNotificationActionView.as_view(), name='admin-notification-action'), # action: approve, cancel, send
    path('notifications/<uuid:pk>/delivery-history/', views.AdminDeliveryHistoryView.as_view(), name='admin-delivery-history'),
]
