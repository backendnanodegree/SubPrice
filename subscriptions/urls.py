from django.urls import path

from subscriptions.views import HistoryListView, MainCreateModalView, MainListView, subscription_update, history_detail, process_ajax 

urlpatterns = [
    path('main/', MainListView.as_view(), name='main'),
    path('main/create/', MainCreateModalView.as_view(), name='main_create'),
    path('main/update/<int:pk>/', subscription_update, name='main_update'),
    path('history/', HistoryListView.as_view(), name='history'),
    path('history/<int:pk>/', history_detail, name='history_detail'),
    path('category_ajax', process_ajax , name='category_ajax'),
    path('service_ajax', process_ajax , name='service_ajax'),
    path('plan_ajax', process_ajax, name='plan_ajax'),
    path('type_ajax', process_ajax , name='type_ajax'),
]