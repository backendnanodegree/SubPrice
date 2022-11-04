from django.urls import path

from subscriptions.views import MainListView

urlpatterns = [
    path('main/', MainListView.as_view(), name='main'),
]