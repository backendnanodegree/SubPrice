from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from alarms.models import Alarm

from subscriptions.models import Billing, Company, Plan, Service, Subscription, Type


class MainListView(TemplateView):
    template_name = "subscriptions/main.html"
    pass

