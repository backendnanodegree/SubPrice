from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from alarms.models import Alarm

from subscriptions.forms import SubscriptionForm
from subscriptions.models import Billing, Company, Plan, Service, Subscription, Type


class MainListView(TemplateView):
    template_name = "subscriptions/main.html"
    pass


class MainCreateModalView(FormView):
    template_name = "subscriptions/main_create.html"
    form_class = SubscriptionForm
    success_url = "/subscriptions/main/"

