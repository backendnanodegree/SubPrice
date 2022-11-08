from django.contrib import admin
from alarms.models import Alarm, AlarmHistory
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Register your models here.

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    """
    최선우 : Alarm Model을 Admin Site에 등록
    """
    list_display = ["subscription", "get_billing_at", "get_dday", "get_date"]
    
    @admin.display(description="다음 결제 예정일")
    def get_billing_at(self, obj):
        """
        결제 예정일 : 구독 시작일로부터 갱신일자를 추출 후, 현재 날짜와 비교하여 계산
                      - 발송 예정일 계산을 위해 'next_billing_at'을 전역 변수로 선언
        """
        global next_billing_at
        renewal_day = obj.subscription.started_at.day
        today = datetime.now() + relativedelta(hours=9)
        pay_year, pay_month, pay_day = today.year, today.month, renewal_day
        
        if renewal_day < today.day:
            if today.month == 12:
                pay_year += 1
                pay_month = 1
            else:
                pay_month += 1    
                
        next_billing_at = datetime(pay_year, pay_month, pay_day).date()
        return next_billing_at
    
    @admin.display(description="메일 발송 설정")
    def get_dday(self, obj):
        return obj.get_d_day_display()
    
    @admin.display(description="발송 예정일")
    def get_date(self, obj):
        return next_billing_at - relativedelta(days=obj.d_day)
    

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
        created_at = obj.created_at + relativedelta(hours=9)
        return created_at.strftime("%Y-%m-%d %H시 %M분")