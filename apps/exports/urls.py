from django.urls import path
from apps.exports.views import ExportTriggerView, ExportHistoryView

urlpatterns = [
    path("trigger/", ExportTriggerView.as_view(), name="export-trigger"),
    path("history/", ExportHistoryView.as_view(), name="export-history"),
]