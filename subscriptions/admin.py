from django.contrib import admin
from django.core.checks import messages

from subscriptions.models import (Type, Company, Billing, Category, 
                                  Service, Plan, Subscription)

from datetime import datetime, date


# Register your models here.

admin.site.register(Type)


admin.site.register(Company)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "company"]
  
    
admin.site.register(Category)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
   
    
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "service", "price"]
  
    
@admin.register(Subscription)
class subscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "get_category", "plan", "billing", "started_at", "get_billing_at", "expire_at", "is_active"]
    search_fields = ["user__email"]
    actions = ["activate_change"]

    @admin.display(description="카테고리")
    def get_category(self, obj):
        return obj.plan.service.category

    def check_target(self, obj):
        if obj.user.is_active == False or obj.is_active == False:
            return "발송 대상 제외" 
    
    @admin.display(description="다음 결제 예정일")
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