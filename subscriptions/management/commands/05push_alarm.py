from alarms.models import Alarm
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

        # 구독 정보 조회
        subscription_list = Subscription.objects.all()
        
        # D-DAY 선택
        dday_list = [-1, 1, 2, 3, 4, 5, 6, 7]
        
    # 데이터 생성
        # 알림 정보 데이터 생성
        for idx, subscription in enumerate(subscription_list):
            d_day = choices(dday_list, weights=[7,1,1,1,1,1,1,1], k=1)[0]
            Alarm.objects.create(d_day=d_day, subscription=subscription)