from django.urls import path

from subscriptions.views import MainCreateModalView, MainListView

urlpatterns = [
    path('main/', MainListView.as_view(), name='main'),
    path('main/create/', MainCreateModalView.as_view(), name='main_create'),
]