import csv
import pandas as pd

from users.models import User
from alarms.models import Alarm
from subscriptions.models import Type, Company, Billing, Category, Service, Plan, Subscription
from django.core.management.base import BaseCommand

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH CSV DB"

    # test 목적의 파일
    # 아래에 코드를 작성하여 터미널 창에 'python manage.py testgo' 입력하여 실행 결과 확인
    def handle(self, *args, **options):

        # BASE_DIR = './static/csv/'

        # company_csv = BASE_DIR + 'company.csv'
        # service_csv = BASE_DIR + 'service.csv'
        # plan_csv = BASE_DIR + 'plan.csv'

        # csv_list = [company_csv, service_csv, plan_csv]
        # data_list = [None, None, None, None]

        # for i in range(3):
        #     with open(csv_list[i], 'rt', encoding='UTF8') as f:
        #         dr = csv.DictReader(f)
        #         data_list[i] = pd.DataFrame(dr)

        # company_data, service_data, plan_data = data_list[0], data_list[1], data_list[2]

        # company_list = company_data.to_records(index=False).tolist()
        # service_list = service_data.iloc[:,[0,1]].to_records(index=False).tolist()
        # plan_list = plan_data.iloc[:,[0,1]].to_records(index=False).tolist()

        # print(plan_list)

        # category = 1  # ajax에서 GET요청 하면서 넘어온 json타입의 데이터를 가공합니다.
        # service = Service.objects.filter(category=category).values_list('id', 'name')
        # print(f"service:{service}")
        # print(f"type(service):{type(service)}")
        # service_list = list(service)
        # print(f"service_list:{service_list}")
        # print(f"type(service_list):{type(service_list)}")

        # plan = Plan.objects.get(id=5)
        # print(plan.price)

        # company_list = list(Company.objects.all().values_list('id', 'company'))
        # print(company_list)

        # account_list = company_list[:19]
        # credit_card_list = company_list[19:38]
        # check_card_list = company_list[19:37]
        # easy_payment_list = company_list[38:52]
        # mobile_payment_list = company_list[45:46] + company_list[52:57]
        # # credit_card = list(range(20,39))
        # # check_card = list(range(20,38))
        # # easy_payment = list(range(39,53))
        # # mobile_payment = [46] + list(range(53,58))
        # print(f"account_list:{account_list}")
        # print(f"credit_card_list:{credit_card_list}")
        # print(f"check_card_list:{check_card_list}")
        # print(f"easy_payment_list:{easy_payment_list}")
        # print(f"mobile_payment_list:{mobile_payment_list}")

        # company_list = list(Company.objects.all().values_list('id', 'company'))
        # CREDIT_CARD, CHECK_CARD, ACCOUNT, EASY_PAYMENT, MOBILE_PAYMENT = 1, 2, 3, 4, 5
        # company_type = {CREDIT_CARD:company_list[19:38],CHECK_CARD:company_list[19:37],ACCOUNT:company_list[:19],
        #                 EASY_PAYMENT:company_list[38:52], MOBILE_PAYMENT:company_list[45:46] + company_list[52:57]}
        # print(company_type[1])

        # subscription = Subscription.objects.filter(id=3).values()
        # print(subscription)

        # subscription_1 = Subscription.objects.filter(id=1)
        # print(f"subscription_1.values():{subscription_1.values()}")
        # print(subscription_1.query)
        # subscription_2 = Subscription.objects.filter(id=1).select_related('plan', 'billing', 'alarm_subscription')
        # print(f"subscription_2.values():{subscription_2.values()}")
        # print(subscription_2.query)

        user = User.objects.get(id=1)

        subscription = Subscription.objects.select_related('plan', 'billing', 'alarm_subscription').get(id=1)
        # Assign fields to use
        # started_at = subscription.started_at
        # expire_at = subscription.expire_at
        # plan_name = subscription.plan.name
        # plan_price = subscription.plan.price

        # # service table
        # service = Service.objects.select_related('category').get(id=subscription.plan.service_id)
        # # Assign fields to use
        # service_name = service.name
        # category_name = service.category.get_category_type_display()

        # # billing table
        # billing = Billing.objects.select_related('type', 'company').get(id=subscription.billing_id)
        # # Assign fields to use
        # method_type = billing.type.get_method_type_display()
        # company_name = billing.company.company

        # # Assign fields to use
        # d_day = subscription.alarm_subscription.get_d_day_display()

        # print(category_name)
        # print(service_name)
        # print(plan_name)
        # print(started_at)
        # print(expire_at)
        # print(plan_price)
        # print(method_type)
        # print(company_name)
        # print(d_day)

        plan = subscription.plan
        
        billing = subscription.billing
        company = billing.company

        print(plan)
        print(billing)
        print(company)