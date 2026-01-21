from django.urls import path

from apps.analytics.views.dashboard import CashflowView, DashboardAnalyticsView

urlpatterns = [
    path("dashboard/", DashboardAnalyticsView.as_view()),
    path("cashflow/", CashflowView.as_view()),
]
