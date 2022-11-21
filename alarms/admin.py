from django.contrib import admin
from alarms.models import Alarm, AlarmHistory
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# Register your models here.

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    """
    최선우 : Alarm Model을 Admin Site에 등록
    """
    list_display = ["subscription", "get_started_at", "get_expire_at", "get_billing_at", "get_dday", "get_date"]
    search_fields = ["subscription__user__email"]

    @admin.display(description="최초 구독일")
    def get_started_at(self, obj):
        return obj.subscription.started_at

    @admin.display(description="구독 만료일")
    def get_expire_at(self, obj):
        return obj.subscription.expire_at

    @admin.display(description="다음 결제 예정일")
    def get_billing_at(self, obj):
        """
        결제 예정일 : 구독 시작일로부터 갱신일자를 추출 후, 현재 날짜와 비교하여 계산
                      - 발송 예정일 계산을 위해 'next_billing_at'을 전역 변수로 선언
        """
        global next_billing_at
        if obj.subscription.is_active == False:
            return None
        else:
            renewal_day = obj.subscription.started_at.day
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
    
    @admin.display(description="메일 발송 설정")
    def get_dday(self, obj):
        if obj.subscription.is_active == False:
            return None
        return obj.get_d_day_display()
    
    @admin.display(description="발송 예정일")
    def get_date(self, obj):
        if obj.subscription.is_active == False: 
            return None
        if obj.d_day > 0 :
            return next_billing_at - relativedelta(days=obj.d_day)
        else:
            return None
    

@admin.register(AlarmHistory)
class AlarmHistoryAdmin(admin.ModelAdmin):
    """
    최선우 : AlarmHistory Model을 Admin Site에 등록
    """
    list_display = ["alarm", "get_date", "get_content", "is_success", "traceback"]
    
    
    @admin.display(description="알림 내역")
    def get_content(self, obj):
        return obj.content[:30]
    
    @admin.display(description="발송 일자")
    def get_date(self, obj):
        created_at = obj.created_at
        return created_at.strftime("%Y-%m-%d %H시 %M분")