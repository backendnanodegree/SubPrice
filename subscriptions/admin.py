from django.contrib import admin
from django.core.checks import messages
from django.utils.html import format_html

from subscriptions.models import (Type, Company, Billing, Category, 
                                  Service, Plan, Subscription)

from datetime import datetime, date


# Register your models here.

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ["method_type", "get_company_list"]

    @admin.display(description="해당 유형의 결제사 목록")
    def get_company_list(self, obj):

        total_company_list = Company.objects.all()

        credit_card = list(range(20,39))
        check_card = list(range(20,38))
        account = list(range(1,20))
        easy_payment = list(range(39,53))
        mobile_payment = [46] + list(range(53,58))
        
        if obj.method_type == 1 :       # 결제 유형이 '신용카드'인 경우
            company_list = total_company_list.filter(id__in=credit_card)
        elif obj.method_type == 2 :     # 결제 유형이 '체크카드'인 경우
            company_list = total_company_list.filter(id__in=check_card)
        elif obj.method_type == 3 :     # 결제 유형이 '계좌이체'인 경우
            company_list = total_company_list.filter(id__in=account)
        elif obj.method_type == 4 :     # 결제 유형이 '간편결제'인 경우
            company_list = total_company_list.filter(id__in=easy_payment)
        elif obj.method_type == 5 :     # 결제 유형이 '휴대폰결제'인 경우
            company_list = total_company_list.filter(id__in=mobile_payment)
        company_name_list = list(company_list.values_list('company', flat=True))
        return format_html(f'<p>{", ".join(company_name_list)}</p>')


admin.site.register(Company)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ["user", "get_total_billing", "get_fullname", "type", "company", "created_at"]
    search_fields = ["user__email", "user__fullname"]

    @admin.display(description="등록된 결제수단 개수")
    def get_total_billing(self, obj):
        billing_list = Billing.objects.filter(user=obj.user)
        return f'{billing_list.count()}개'
    
    @admin.display(description="이름")
    def get_fullname(self, obj):
        return obj.user.fullname
  
    
admin.site.register(Category)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
   
    
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "get_category", "service", "get_price"]

    @admin.display(description="카테고리")
    def get_category(self, obj):
        return obj.service.category.get_category_type_display()

    @admin.display(description="월 구독료")
    def get_price(self, obj):
        return format(obj.price,',')+"원"
  
    
@admin.register(Subscription)
class subscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "get_subscription_cnt", "get_category", "get_plan_name", "get_plan_price", "get_billing", "started_at", "get_billing_at", "expire_at", "is_active", "delete_on"]
    search_fields = ["user__email"]
    actions = ["activate_change", "delete_change", "activate_refresh"]

    @admin.display(description="total / ing")
    def get_subscription_cnt(self, obj):
        subscription_total_cnt = Subscription.objects.filter(user=obj.user).count()
        subscription_ing_cnt = Subscription.objects.filter(user=obj.user, is_active=True).count()
        return f'{subscription_total_cnt}개 / {subscription_ing_cnt}개'

    @admin.display(description="카테고리")
    def get_category(self, obj):
        return obj.plan.service.category

    @admin.display(description="서비스 유형")
    def get_plan_name(self, obj):
        return obj.plan.name

    @admin.display(description="월 구독료")
    def get_plan_price(self, obj):
        return format(obj.plan.price,',')+"원"

    @admin.display(description="결제 정보")
    def get_billing(self, obj):
        company = obj.billing.company.company
        billing_type = obj.billing.type.get_method_type_display()[:-2]
        return company + " - " + billing_type

    def check_target(self, obj):
        if obj.user.is_active == False or obj.delete_on == True or obj.is_active == False:
            return "발송 대상 제외" 
    
    @admin.display(description="결제 예정일")
    def get_billing_at(self, obj):
        if self.check_target(obj) == "발송 대상 제외":
            return None
        return obj.next_billing_at()

    @admin.display(description="구독정보 활성 여부 변경")
    def activate_change(self, request, queryset):
        activate_cnt = 0
        deactivate_cnt = 0

        for item in queryset:
            active_status = item.is_active
            item.is_active = 1-active_status
            item.save()
            if active_status == 1:
                activate_cnt += 1
            else:
                deactivate_cnt += 1

        if activate_cnt and deactivate_cnt:
            message = f"{activate_cnt} 개의 구독정보를 비활성화 / {deactivate_cnt} 개의 구독정보를 활성화 하였습니다."
        elif activate_cnt:
            message = f"{activate_cnt} 개의 구독정보를 비활성화 하였습니다."
        elif deactivate_cnt:
            message = f"{deactivate_cnt} 개의 구독정보를 활성화 하였습니다."

        self.message_user(request, message, level=messages.INFO)


    @admin.display(description="구독정보 삭제/사용 처리")
    def delete_change(self, request, queryset):
        use_cnt = 0
        delete_cnt = 0

        for item in queryset:
            delete_status = item.delete_on
            item.delete_on = 1-delete_status
            item.save()
            if delete_status == 1:
                use_cnt += 1
            else:
                delete_cnt += 1

        if use_cnt and delete_cnt:
            message = f"{use_cnt} 개의 구독정보를 삭제 처리 / {delete_cnt} 개의 구독정보를 사용 처리 하였습니다."
        elif use_cnt:
            message = f"{use_cnt} 개의 구독정보를 삭제 처리 하였습니다."
        elif delete_cnt:
            message = f"{delete_cnt} 개의 구독정보를 사용 처리 하였습니다."

        self.message_user(request, message, level=messages.INFO)

    @admin.display(description="구독정보 활성 여부 갱신")
    def activate_refresh(self, request, queryset):
        total_cnt = queryset.count()
        today = datetime.now().date()

        target_cnt = 0

        for item in queryset:
            if item.is_active == True and item.expire_at and item.expire_at < today:
                item.is_active = False
                item.save()
                target_cnt += 1

        message = f"{total_cnt} 개의 구독정보에 대한 활성 여부를 갱신 하였으며, 총 {target_cnt} 개의 구독정보가 비활성화 되었습니다."

        self.message_user(request, message, level=messages.INFO)