from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from alarms.models import Alarm

from datetime import datetime,  date

from subscriptions.forms import SubscriptionForm
from subscriptions.models import Billing, Company, Plan, Service, Subscription, Type

# custom decorator
def check_permissions(function):
    def decorator_func(request, pk):
        if request.user.is_anonymous:
            return redirect("login")
        else:
            subscription_user = Subscription.objects.get(id=pk).user
            if request.user!= subscription_user:
                return redirect("main")
        return function(request, pk)

    return decorator_func


@method_decorator(login_required(login_url="/login/"), name="get")
class MainListView(TemplateView):
    template_name = "subscriptions/main.html"

    def get_context_data(self, **kwargs):

        # display none header.html
        context = {}
        context['show_header'] = True

        user = self.request.user

        # subscription table
        subscription = list(Subscription.objects.filter(user=user, is_active=1, delete_on=0))
        subscription.sort(key=lambda x: x.next_billing_at(), reverse=True)

        context['subscription_qs'] = subscription

        # Pagination
        paginator = Paginator(object_list=subscription, per_page=5)
        page = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page)
        page_num_list = [num for num in range(1, page_obj.paginator.num_pages + 1)]

        subscription_empty_row_count = 5-len(subscription)%5
        if not len(subscription)%5 and len(subscription)!=0:
            subscription_empty_row_count = 0

        context["page"] = page
        context["page_obj"] = page_obj
        context["page_num_list"] = page_num_list
        
        if int(page) == page_num_list[-1]:
            context['subscription_empty_row_count'] = subscription_empty_row_count
        else:
            context['subscription_empty_row_count'] = 0

        # expire model
        expire = Subscription.objects.filter(user=user, is_active=0, delete_on=0).order_by("-expire_at")

        if expire.count() >= 5 :
            expire = expire[:5]
        else:
            expire_empty_row_count = 5 - expire.count()
            context['expire_empty_row_count'] = expire_empty_row_count

        context['expire_qs'] = expire

        return context

@method_decorator(login_required(login_url="/login/"), name="get")
class MainCreateModalView(FormView):
    template_name = "subscriptions/main_create.html"
    form_class = SubscriptionForm
    success_url = "/subscriptions/main/"

    def form_valid(self, form):      

        user = self.request.user

        category_type = form.data.get('category_type')
        service_type = form.data.get("service_type")
        plan_type = form.data.get("plan_type")
        started_at = form.data.get("started_at")
        expire_at = form.data.get("expire_at")
        company_type = form.data.get("company_type")
        method_type = form.data.get("method_type")
        d_day = form.data.get("d_day")
        service = Service.objects.get(id=service_type)
        plan = Plan.objects.get(id=plan_type)

        # billing 데이터 저장
        company = Company.objects.get(id=company_type)
        type = Type.objects.get(method_type=method_type)
        billing, is_created = Billing.objects.get_or_create(
            user = user,
            type = type,
            company = company,
        )
        
        # subscription 데이터 저장
        subscription = Subscription.objects.create(
            user=user,
            plan=plan, 
            billing=billing, 
            started_at=started_at,
        )

        if expire_at == '':
            subscription.expire_at = None
        else:
            if datetime.strptime(expire_at, "%Y-%m-%d").date() < datetime.now().date():
                subscription.is_active = False

        subscription.save()

        # alarm 데이터 저장
        alarm, is_created = Alarm.objects.get_or_create(
            d_day = d_day,
            subscription = subscription,
        )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@check_permissions
def subscription_update(request, pk):

    # Assign object to use
    user = request.user

    # subscription table
    subscription = Subscription.objects.get(id=pk)
    # Assign fields to use
    started_at = subscription.started_at
    expire_at = subscription.expire_at

    # plan table
    plan = Plan.objects.get(id=subscription.plan.id)
    # Assign fields to use
    plan_type = plan.id
    price = plan.price
    category_type = plan.service.category.category_type

    # Assign fields to use
    service_type = plan.service.id

    # billing/company/type table
    billing = Billing.objects.get(id=subscription.billing.id)
    type_object = Type.objects.get(id=billing.type.id)
    # Assign fields to use
    company_type = billing.company.id
    method_type = type_object.method_type

    # alarm table
    alarm = Alarm.objects.get(subscription=subscription)
    # Assign fields to use
    d_day = alarm.d_day

    # Existing data
    data={
        "category_type":category_type, "service_type":service_type, 
        "plan_type":plan_type, "price":price, 
        "started_at":started_at, "expire_at":expire_at, 
        "company_type":company_type, "method_type":method_type, 
        "d_day":d_day
    }

    if request.method == 'POST':
        form = SubscriptionForm(request.POST,initial=data)
        
        # form : valid
        if form.is_valid():

            # Input data
            category_type = form.data.get('category_type')
            service_type = form.data.get("service_type")
            plan_type = form.data.get("plan_type")
            started_at = form.data.get("started_at")
            expire_at = form.data.get("expire_at")
            company_type = form.data.get("company_type")
            method_type = form.data.get("method_type")
            d_day = form.data.get("d_day")

            # Query existing data for input data
            service = Service.objects.get(id=service_type)
            plan = Plan.objects.get(service=service, id=plan_type)
            
            # Query existing data for input data
            type_object = Type.objects.get(method_type=method_type)
            company = Company.objects.get(id=company_type)
            # Update billing data with input data
            billing, is_created = Billing.objects.get_or_create(
                user = user,
                type = type_object,
                company = company,
            )

            # Update subscription data with input data
            subscription.plan = plan
            subscription.billing = billing
            subscription.started_at = started_at
            if expire_at == '':
                expire_at = None
            else:
                expire_at = date(*map(int,expire_at.split("-")))
            subscription.expire_at = expire_at
            if expire_at != None:
                if expire_at < datetime.now().date():
                    subscription.is_active = False
                elif expire_at >= datetime.now().date():
                    subscription.is_active = True
            else:
                subscription.is_active = True
            subscription.save()

            # Update alarm data with input data
            alarm.d_day = d_day
            alarm.save()
            
            if 'main' in request.resolver_match.url_name:
                return redirect("main")
            else:
                return redirect("history")

        # form : invalid
        else:
            context= {'form': form, 'pk': pk}
            if 'main' in request.resolver_match.url_name:
                return render(request, 'subscriptions/main_update.html', context)
            else:
                return render(request, 'subscriptions/history_update.html', context)

    else:
        form = SubscriptionForm(initial=data)
    context= {'form': form, 'pk': pk}
    if 'main' in request.resolver_match.url_name:
        return render(request, 'subscriptions/main_update.html', context)
    else:
        return render(request, 'subscriptions/history_update.html', context)

@method_decorator(login_required(login_url="/login/"), name="get")
class HistoryListView(TemplateView):
    template_name = "subscriptions/history.html"

    def get_context_data(self, **kwargs):

        # display none header.html
        context = {}
        context['show_header'] = True

        user = self.request.user

        # history table
        subscription = list(Subscription.objects.filter(user=user, is_active=1, delete_on=0))
        subscription.sort(key=lambda x: x.next_billing_at(), reverse=True)
        
        expire = list(Subscription.objects.filter(user=user, is_active=0, delete_on=0))
        expire.sort(key=lambda x: x.expire_at, reverse=True)
        
        history = list(subscription) + list(expire)

        # Pagination
        paginator = Paginator(object_list=history, per_page=10)
        page = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page)
        page_num_list = [num for num in range(1, page_obj.paginator.num_pages + 1)]

        history_empty_row_count = 10-len(history)%10
        if not len(history)%10 and len(history)!=0:
            history_empty_row_count = 0

        context["page"] = page
        context["page_obj"] = page_obj
        context["page_num_list"] = page_num_list
        
        if int(page) == page_num_list[-1]:
            context['history_empty_row_count'] = history_empty_row_count
        else:
            context['history_empty_row_count'] = 0
        
        return context

    def post(self, request):

        # delete subscription id list
        list_selected = request.POST.getlist('selected')
        
        # delete subscription info
        subscription = Subscription.objects.filter(id__in=list_selected)
        subscription.update(delete_on=1)
        
        return redirect('history')

@check_permissions
def history_detail(request, pk):

    # Assign object to use
    user = request.user

    # subscription table
    subscription = Subscription.objects.select_related('user', 'plan', 'billing', 'alarm_subscription').get(id=pk)
    # Assign fields to use
    started_at = subscription.started_at
    expire_at = subscription.expire_at
    plan_name = subscription.plan.name
    plan_price = format(subscription.plan.price,',')+"원"

    # service table
    service = Service.objects.select_related('category').get(id=subscription.plan.service_id)
    # Assign fields to use
    service_name = service.name
    category_name = service.category.get_category_type_display()

    # billing table
    billing = Billing.objects.select_related('type', 'company').get(id=subscription.billing_id)
    # Assign fields to use
    method_type = billing.type.get_method_type_display()
    company_name = billing.company.company

    # Assign fields to use
    d_day = subscription.alarm_subscription.get_d_day_display()

    # Existing data
    data=[category_name, service_name, plan_name, started_at, expire_at, 
          plan_price, method_type, company_name, d_day]

    context= {'data': data, 'pk': pk}
    return render(request, 'subscriptions/history_detail.html', context)

def process_ajax(request) -> JsonResponse:
    if request.GET.get('category_val'):
        category = request.GET.get('category_val')
        result = list(Service.objects.filter(category__category_type=category).values_list('id', 'name'))
    elif request.GET.get('service_val'):
        service = request.GET.get('service_val')
        result = list(Plan.objects.filter(service=service).values_list('id', 'name'))
    elif request.GET.get('plan_val'):
        plan_id = request.GET.get('plan_val')
        result = Plan.objects.get(id=plan_id).price
    elif request.GET.get('method_val'):
        company_list = list(Company.objects.all().values_list('id', 'company'))
        DEFAULT, CREDIT_CARD, CHECK_CARD, ACCOUNT, EASY_PAYMENT, MOBILE_PAYMENT = 0, 1, 2, 3, 4, 5
        company_type = {DEFAULT:company_list[0:1], CREDIT_CARD:company_list[20:39],CHECK_CARD:company_list[20:38],
                        ACCOUNT:company_list[1:20], EASY_PAYMENT:company_list[39:53], 
                        MOBILE_PAYMENT:company_list[46:47] + company_list[53:58]}
        method_val = int(request.GET.get('method_val'))
        result = company_type[method_val]
    return JsonResponse(result, safe=False)