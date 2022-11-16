from django.contrib import admin
from subscriptions.models import (Type, Company, Billing, Category, 
                                  Service, Plan, Subscription)

from django.utils import timezone
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


# Register your models here.

admin.site.register(Type)
""" 최선우 : Type Model을 Admin Site에 등록 """


admin.site.register(Company)
""" 최선우 : Company Model을 Admin Site에 등록 """


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    """
    최선우 : Billing Model을 Admin Site에 등록
    """
    list_display = ["user", "type", "company"]
  
    
admin.site.register(Category)
""" 최선우 : Category Model을 Admin Site에 등록 """


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    최선우 : Service Model을 Admin Site에 등록
    """
    list_display = ["name", "category"]
   
    
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """
    최선우 : Plan Model을 Admin Site에 등록
    """
    list_display = ["name", "service", "price"]
  
    
@admin.register(Subscription)
class subscriptionAdmin(admin.ModelAdmin):
    """
    최선우 : Subscription Model을 Admin Site에 등록
    """
    list_display = ["user", "get_category", "plan", "billing", "started_at", "get_billing_at", "expire_at", "is_active"]
    
    @admin.display(description="카테고리")
    def get_category(self, obj):
        try:
            return obj.plan.service.category
        except:
            return None
    
    @admin.display(description="다음 결제 예정일")
    def get_billing_at(self, obj):
        """
        결제 예정일 : 구독 시작일로부터 갱신일자를 추출 후, 현재 날짜와 비교하여 계산
        """
        
        if obj.is_active == False:
            return None
        else:
            renewal_day = obj.started_at.day
            today = timezone.now()
            today_day = today.day
            pay_year, pay_month, pay_day = today.year, today.month, renewal_day
            
            if renewal_day < today.day:
                if today.month == 12:
                    pay_year += 1
                    pay_month = 1
                else:
                    pay_month += 1    
            try:        
                next_billing_at = date(pay_year, pay_month, pay_day)
            except:
                try:
                    next_billing_at = date(pay_year, pay_month, pay_day-1)
                except:
                    try:
                        next_billing_at = date(pay_year, pay_month, pay_day-2)
                    except:
                        next_billing_at = date(pay_year, pay_month, pay_day-3)
                    
            return next_billing_at