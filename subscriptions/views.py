from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from alarms.models import Alarm

from datetime import datetime,  date

from subscriptions.forms import SubscriptionForm, SubscriptionUpdateForm
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
        subscription = list(Subscription.objects.filter(user=user, is_active=1))
        subscription.sort(key=lambda x: x.next_at(), reverse=True)

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
        expire = Subscription.objects.filter(user=user, is_active=0).order_by("-expire_at")

        if expire.count() >= 5 :
            expire = expire[:5]
        else:
            expire_empty_row_count = 5 - expire.count()

        context['expire_qs'] = expire
        context['expire_empty_row_count'] = expire_empty_row_count

        return context

@method_decorator(login_required(login_url="/login/"), name="get")
class MainCreateModalView(FormView):
    template_name = "subscriptions/main_create.html"
    form_class = SubscriptionForm
    success_url = "/subscriptions/main/"

    def form_valid(self, form):      

        user = self.request.user

        service = form.data.get("service")
        plan = form.data.get("plan")
        started_at = form.data.get("started_at")
        expire_at = form.data.get("expire_at")
        company = form.data.get("company")
        type_object = form.data.get("type_object")
        alarm = form.data.get("alarm")
        service = Service.objects.get(name=service)
        plan = Plan.objects.get(service=service, name=plan)

        # billing 데이터 저장
        company = Company.objects.get(company=company)
        type = Type.objects.get(method_type=type_object)
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
            subscription.expire_at=expire_at

        subscription.save()

        # alarm 데이터 저장
        alarm, is_created = Alarm.objects.get_or_create(
            d_day = alarm,
            subscription = subscription,
        )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


# @login_required(login_url="login")
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
    plan_name = plan.name
    price = plan.price
    category = plan.service.category.category_type

    # category table
    category_type = plan.service.category.get_category_type_display()
    # Assign fields to use
    service_name = plan.service

    # billing/company/type table
    billing = Billing.objects.get(id=subscription.billing.id)
    company = Company.objects.get(id=billing.company.id)
    type_object = Type.objects.get(id=billing.type.id)
    # Assign fields to use
    method_type = type_object.method_type

    # alarm table
    alarm = Alarm.objects.get(subscription=subscription)
    # Assign fields to use
    d_day = alarm.d_day

    # Existing data
    data={
        "category_type":category, "service_name":service_name, 
        "plan_name":plan_name, "price":price, 
        "started_at":started_at, "expire_at":expire_at, 
        "company":company, "method_type":method_type, 
        "d_day":d_day
    }

    # price information setting
    price_ = format(price,',')+"원" 

    if request.method == 'POST':
        form = SubscriptionUpdateForm(request.POST,initial=data)\
        
        # form : valid
        if form.is_valid():

            # Input data
            service_name = form.data.get("service_name")
            plan_name = form.data.get("plan_name")
            started_at = form.data.get("started_at")
            service_name = form.data.get("service_name")
            expire_at = form.data.get("expire_at")
            company = form.data.get("company")
            method_type = form.data.get("method_type")
            d_day = form.data.get("d_day")

            # Query existing data for input data
            service = Service.objects.get(name=service_name)
            plan = Plan.objects.get(service=service, name=plan_name)
            
            # Query existing data for input data
            type_object = Type.objects.get(method_type=method_type)
            company = Company.objects.get(company=company)
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
            
            return redirect("main")

        # form : invalid
        else:
            context= {'form': form, 'pk': pk, 'category_type': category_type, 'price_': price_}
            return render(request, 'subscriptions/main_update.html', context)

    else:
        form = SubscriptionUpdateForm(initial=data)
    context= {'form': form, 'pk': pk, 'category_type': category_type, 'price_': price_}
    return render(request, 'subscriptions/main_update.html', context)