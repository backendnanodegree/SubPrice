from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from alarms.models import Alarm

from subscriptions.forms import SubscriptionForm
from subscriptions.models import Billing, Company, Plan, Service, Subscription, Type


class MainListView(TemplateView):
    template_name = "subscriptions/main.html"

    def get_context_data(self, **kwargs):

        # display none header.html
        context = {}
        context['show_header'] = True

        user = self.request.user
        
        # subscription table
        subscription = Subscription.objects.filter(user=user, is_active=1).order_by("-started_at")
        context['subscription_qs'] = subscription

        # Pagination
        paginator = Paginator(object_list=subscription, per_page=5)
        page = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page)
        page_num_list = [num for num in range(1, page_obj.paginator.num_pages + 1)]
        
        subscription_empty_row_count = 5-(subscription.count())%5
        if not subscription.count()%5 and subscription.count()!=0:
            subscription_empty_row_count = 0

        context["page"] = page
        context["page_obj"] = page_obj
        context["page_num_list"] = page_num_list
        
        if int(page) == page_num_list[-1]:
            context['subscription_empty_row_count'] = subscription_empty_row_count
        else:
            context['subscription_empty_row_count'] = 0

        # expire model
        expire = Subscription.objects.filter(user=user, is_active=0).order_by("-expire_at")

        if expire.count() >= 5 :
            expire = expire[:5]
        else:
            expire_empty_row_count = 5 - expire.count()

        context['expire_qs'] = expire
        context['expire_empty_row_count'] = expire_empty_row_count

        return context


class MainCreateModalView(FormView):
    template_name = "subscriptions/main_create.html"
    form_class = SubscriptionForm
    success_url = "/subscriptions/main/"

