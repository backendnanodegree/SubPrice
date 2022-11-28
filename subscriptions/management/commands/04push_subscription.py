from subscriptions.models import Billing, Plan, Subscription
from users.models import User
from django.core.management.base import BaseCommand
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from random import *

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH SUBSCRIPTION DB"

    def handle(self, *args, **options):
        
        # 생성할 subscription 수
        number = int(input("생성할 subscription의 수를 입력하세요 : "))
        
        # 현재 일자 계산
        now = datetime.now().date()
        
        # 유저, 구독플랜 리스트 작성
        user_list = User.objects.all()
        plan_list = Plan.objects.all()
        
        year_list = list(range(2017,2023))
        month_list = list(range(1,13))
        day_list = [list(range(1,29)), list(range(1,30)), 
                    list(range(1,31)), list(range(1,32))]
        
        # 사용자 구독 정보 등록
        cnt = 0
        
        while cnt < number:
            
            # 유저 추출
            user = choice(user_list)
            
            # 한 유저당 20개까지만 구독정보 등록
            subscription_list = Subscription.objects.filter(user=user)
            if len(subscription_list) == 20:
                continue
                
            #유저에 따른 결제수단 추출
            billing_list = Billing.objects.filter(user=user)
            billing = choice(billing_list)
        
            # 구독플랜 추출
            plan = choice(plan_list)
            
            # 구독 시작일 추출
            start_year = choice(year_list)
            start_month = choice(month_list)
            if start_month in [1,3,5,7,8,10,12]:
                start_day = choice(day_list[3])
            elif start_month == 2:
                if start_year % 4 != 0:
                    start_day = choice(day_list[0])
                else:
                    start_day = choice(day_list[1])
            else:
                start_day = choice(day_list[2])
                    
            started_at = date(start_year, start_month, start_day)
            
            # 구독 종료일 추출
            end_schedule = choice([True,False])
            end_month_period = choice(list(range(1,61)))
            if end_schedule == False:
                expire_at = None
            else:
                expire_at = started_at + relativedelta(months=end_month_period)
                
            # 활성 여부 계산
            if end_schedule and expire_at < now:
                is_active = False
            else:
                is_active = True
            
            Subscription.objects.get_or_create( \
                            user=user, plan=plan, billing=billing, started_at=started_at, 
                            expire_at=expire_at, is_active=is_active)
            
            cnt += 1