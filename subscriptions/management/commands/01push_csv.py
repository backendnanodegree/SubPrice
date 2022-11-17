import csv
import pandas as pd

from subscriptions.models import Type, Company, Category, Service, Plan
from django.core.management.base import BaseCommand

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH CSV DB"

    def handle(self, *args, **options):
        
        # 폴더 경로 지정
        #   manage.py 파일 위치 기준으로 절대경로 지정
        BASE_DIR = './subscriptions/management/csv/'
        
        # Type 모델 데이터
        with open(BASE_DIR + 'type.csv', 'rt', encoding='UTF8') as f:
            dr = csv.DictReader(f)
            data = pd.DataFrame(dr)

        for row in data.itertuples():
            try:
                Type.objects.get_or_create(id=row[1], method_type=row[2])
            except:
                continue
        
        # Company 모델 데이터    
        with open(BASE_DIR + 'company.csv', 'rt', encoding='UTF8') as f:
            dr = csv.DictReader(f)
            data = pd.DataFrame(dr)
        
        for row in data.itertuples():
            try:
                Company.objects.get_or_create(id=row[1], company=row[2])
            except:
                continue
            
        # Category 모델 데이터    
        with open(BASE_DIR + 'category.csv', 'rt', encoding='UTF8') as f:
            dr = csv.DictReader(f)
            data = pd.DataFrame(dr)
        
        for row in data.itertuples():
            try:
                Category.objects.get_or_create(id=row[1], category_type=row[2])
            except:
                continue
            
        # Service 모델 데이터    
        with open(BASE_DIR + 'service.csv', 'rt', encoding='UTF8') as f:
            dr = csv.DictReader(f)
            data = pd.DataFrame(dr)
        
        for row in data.itertuples():
            try:
                Service.objects.get_or_create(id=row[1], name=row[2], category_id=row[3])
            except:
                continue
            
        # Plan 모델 데이터    
        with open(BASE_DIR + 'plan.csv', 'rt', encoding='UTF8') as f:
            dr = csv.DictReader(f)
            data = pd.DataFrame(dr)
        
        for row in data.itertuples():
            try:
                Plan.objects.get_or_create(id=row[1], name=row[2], price=row[3], service_id=row[4])
            except:
                continue