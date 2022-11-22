from django.contrib import admin
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

    @admin.display(description="카테고리")
    def get_category(self, obj):
        return obj.plan.service.category
    
    @admin.display(description="다음 결제 예정일")
    def get_billing_at(self, obj):
        
        if obj.is_active == False:
            return None
        else:
            renewal_day = obj.started_at.day
            today = datetime.now()
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