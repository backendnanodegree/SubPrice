from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class MainListView(TemplateView):
    template_name = 'subscriptions/main.html'
    pass