from django.urls import path
from . import views

urlpatterns = [
    path('feature-snapshots/generate/', views.GenerateFeatureSnapshotView.as_view(), name='ews-feature-snapshot-generate'),
    path('train/', views.TrainModelView.as_view(), name='ews-train'),
    path('assessments/run/', views.RunAssessmentView.as_view(), name='ews-assessment-run'),
    path('assessments/', views.AssessmentListView.as_view(), name='ews-assessment-list'),
    path('assessments/<uuid:pk>/', views.AssessmentDetailView.as_view(), name='ews-assessment-detail'),
    path('assessments/<uuid:pk>/review/', views.ReviewAssessmentView.as_view(), name='ews-assessment-review'),
    path('interventions/', views.InterventionListView.as_view(), name='ews-intervention-list'),
    path('interventions/<uuid:pk>/notes/', views.InterventionNoteCreateView.as_view(), name='ews-intervention-note-create'),
    path('notification-drafts/', views.NotificationDraftCreateView.as_view(), name='ews-notification-draft-create'),
    path('notification-drafts/<uuid:pk>/approve/', views.ApproveNotificationDraftView.as_view(), name='ews-notification-draft-approve'),
]
