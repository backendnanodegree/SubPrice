from django.urls import path

from subscriptions.views import HistoryListView, MainCreateModalView, MainListView, subscription_update

urlpatterns = [
    path('main/', MainListView.as_view(), name='main'),
    path('main/create/', MainCreateModalView.as_view(), name='main_create'),
    path('main/update/<int:pk>/', subscription_update, name='main_update'),
    path('history/', HistoryListView.as_view(), name='history'),
]