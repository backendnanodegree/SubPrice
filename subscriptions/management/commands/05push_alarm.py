from alarms.models import Alarm, AlarmHistory
from subscriptions.models import Type, Company, Billing, Category, Service, Plan, Subscription
from users.models import User
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, date
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from random import *

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH ALARM DB"

    def handle(self, *args, **options):
        
    # 알림 정보

        # 알람 모델이 없는 구독 정보 조회
        all_subscription_id = set(Subscription.objects.all().values_list('id', flat=True))
        has_alarm_subscription_id = set(Alarm.objects.all().values_list('subscription__id', flat=True))
        no_alarm_subscription_id = all_subscription_id - has_alarm_subscription_id
        subscription_list = Subscription.objects.filter(id__in=no_alarm_subscription_id)
        
        # D-DAY 선택
        dday_list = [-1, 1, 2, 3, 4, 5, 6, 7]

    # 알림 내역

        # 알림 발송 여부
        success_list = [0, 1]
        
    # 데이터 생성
        # 알림 정보 데이터 생성
        for idx, subscription in enumerate(subscription_list):
            d_day = choices(dday_list, weights=[3,1,1,1,1,1,1,1], k=1)[0]
            Alarm.objects.get_or_create(d_day=d_day, subscription=subscription)

        # 알림 내역 데이터 생성
        alarm_list = Alarm.objects.all()

        for idx, alarm in enumerate(alarm_list):

            # 유저 정보 확인
            user_name = alarm.subscription.user.fullname
            user_email = alarm.subscription.user.email

            # 구독 정보 확인
            service_name = alarm.subscription.plan.service.name
            plan_name = alarm.subscription.plan.name

            # 결제 정보 확인
            company_name = alarm.subscription.billing.company
            type_name = alarm.subscription.billing.type
            price = alarm.subscription.plan.price
            
            if alarm.d_day > 0:
                n = 1
                while True:
                    next_billing_at = alarm.subscription.started_at + relativedelta(months=n)

                     # 발송 성공 여부
                    is_success = choices(success_list, weights=[1,9], k=1)[0]

                    # 메일 발송일
                    send_email_at = next_billing_at - relativedelta(days=alarm.d_day)

                    # 메일 발송 시각
                    year = send_email_at.year
                    month = send_email_at.month
                    day = send_email_at.day
                    hour = 0
                    minute = choice(range(0,6))
                    second = choice(range(0,60))
                    send_email_time = datetime(year, month, day, hour, minute, second)

                    if send_email_at > timezone.now().date():
                        break

                    if is_success:
                        # 메일 발송 내용
                        content = f"안녕하세요, {user_name}님.\n\n현재 구독 중인 {service_name} {plan_name} 서비스에 대해\n{next_billing_at}에 {company_name} {type_name}를 통해 {price}원 결제 예정입니다.\n참고하시기 바랍니다.\n\n저희 서비스를 이용해주셔서 감사합니다.\n오늘도 좋은 하루 되세요."
                        # 데이터 생성
                        AlarmHistory.objects.create(alarm=alarm, content=content, is_success=is_success)
                    else:
                        # 메일 발송 내용
                        content = ""
                        alarmhistory = AlarmHistory.objects.create(created_at=send_email_time, alarm=alarm)
                        send_email_time1 = send_email_time.strftime("%Y년 %m월 %d일 %I시 %M분 %S초 (%a)")
                        content = f"{send_email_time1}에 {user_name}에게 보낸 알림 메일이 발송에 실패하였습니다.\n\n■ 사용자 구독 정보\n   - 사용자명 : {user_name}\n   - 이메일 주소 : {user_email}\n   - 서비스 : {service_name} / {plan_name}\n   - 결제 예정일 : {next_billing_at}\n   - 결제 수단 : {company_name} {type_name}\n   - 결제 금액 : {price}원"
                        traceback = "추후 갱신 예정"
                        alarmhistory.content = content
                        alarmhistory.traceback = traceback
                        alarmhistory.save()

                    n += 1

