import csv
import pandas as pd

from subscriptions.models import Type, Company, Category, Service, Plan
from django.core.management.base import BaseCommand

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH CSV DB"

    # test 목적의 파일
    # 아래에 코드를 작성하여 터미널 창에 'python manage.py testgo' 입력하여 실행 결과 확인
    def handle(self, *args, **options):

        BASE_DIR = './static/csv/'

        company_csv = BASE_DIR + 'company.csv'
        service_csv = BASE_DIR + 'service.csv'
        plan_csv = BASE_DIR + 'plan.csv'

        csv_list = [company_csv, service_csv, plan_csv]
        data_list = [None, None, None, None]

        for i in range(3):
            with open(csv_list[i], 'rt', encoding='UTF8') as f:
                dr = csv.DictReader(f)
                data_list[i] = pd.DataFrame(dr)

        company_data, service_data, plan_data = data_list[0], data_list[1], data_list[2]

        company_list = company_data.to_records(index=False).tolist()
        service_list = service_data.iloc[:,[0,1]].to_records(index=False).tolist()
        plan_list = plan_data.iloc[:,[0,1]].to_records(index=False).tolist()

        print(plan_list)
