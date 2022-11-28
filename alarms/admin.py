from django.contrib import admin
from django.utils.html import format_html
from django.core.checks import messages

from alarms.models import Alarm, AlarmHistory
from datetime import datetime
from dateutil.relativedelta import relativedelta

import re

# Register your models here.

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ["subscription", "get_started_at", "get_expire_at", "get_billing_at", "get_dday", "get_date", "get_isactive"]
    search_fields = ["subscription__user__email"]

    @admin.display(description="최초 구독일")
    def get_started_at(self, obj):
        return obj.subscription.started_at

    @admin.display(description="구독 만료일")
    def get_expire_at(self, obj):
        return obj.subscription.expire_at

    def check_target(self, obj):
        if obj.subscription.user.is_active == False or obj.subscription.is_active == False:
            return "발송 대상 제외" 
    
    @admin.display(description="결제 예정일")
    def get_billing_at(self, obj):
        if self.check_target(obj) == "발송 대상 제외":
            return None
        return obj.subscription.next_billing_at()
    
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
            return obj.subscription.next_billing_at() - relativedelta(days=obj.d_day)
        else:
            return None

    @admin.display(description="알림 활성 여부")
    def get_isactive(self, obj):
        if obj.subscription.is_active == False or obj.d_day == -1:
            return format_html(f'<img src="/static/admin/img/icon-no.svg" alt="No" style="width:13px; height:13px;">')
        else:
            return format_html(f'<img src="/static/admin/img/icon-yes.svg" alt="Yes" style="width:13px; height:13px;">')
    

@admin.register(AlarmHistory)
class AlarmHistoryAdmin(admin.ModelAdmin):
    list_display = ["get_subscription", "get_renewal_date", "get_renewal_day", "get_d_day", "get_send_date", "get_content"]
    search_fields = ["alarm__subscription__user__email", "alarm__d_day"]
    actions = ["delete_all"]
    
    @admin.display(description="구독 정보")
    def get_subscription(self, obj):
        return obj.alarm.subscription

    @admin.display(description="해당 갱신일자")
    def get_renewal_date(self, obj):
        match = re.search(r'\d{4}-\d{2}-\d{2}', obj.content)
        renewal_date = datetime.strptime(match.group(), '%Y-%m-%d').date()

        return renewal_date

    @admin.display(description="구독 갱신일")
    def get_renewal_day(self, obj):
        return f"매월 {obj.alarm.subscription.started_at.day}일"

    @admin.display(description="알림 지정일")
    def get_d_day(self, obj):
        return f"{obj.alarm.d_day}일 전"
    
    @admin.display(description="발송 일자")
    def get_send_date(self, obj):
        created_at = obj.created_at
        return created_at.strftime("%Y-%m-%d %H시 %M분")

    @admin.display(description="알림 내역")
    def get_content(self, obj):
        return obj.content[:30]

    @admin.display(description="전체 데이터 삭제")
    def delete_all(self, request, queryset):
        alarm_history_list = AlarmHistory.objects.all()
        total_cnt = alarm_history_list.count()
        alarm_history_list.delete()

        message = f"총 {total_cnt} 개의 알림 내역 정보를 모두 삭제하였습니다."

        self.message_user(request, message, level=messages.INFO)