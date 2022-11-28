import csv
import pandas as pd
import boto3
import io
from django.conf import settings

from subscriptions.models import Type, Company, Category, Service, Plan
from django.core.management.base import BaseCommand

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH CSV DB"

    def handle(self, *args, **options):

        # csv 파일 읽어오는 'static' 경로 : config/settings.py에서 설정

        target_list = ["type.csv", "company.csv", "category.csv", "service.csv", "plan.csv"]
        data_list = []

        # 'here' : 프로젝트 폴더 내에서 읽어오기
        if settings.CSV_READ_FROM == 'here':
        
            BASE_DIR = './static/csv/'
            
            csv_list = []

            for target in target_list:
                csv_path = BASE_DIR + target
                csv_list.append(csv_path)

            for csv_file in csv_list:
                with open(csv_file, 'rt', encoding='UTF8') as f:
                    dr = csv.DictReader(f)
                    data_list.append(pd.DataFrame(dr))

        # AMAZON S3 에서 읽어오기
        elif settings.CSV_READ_FROM == 's3':

            aws_access_key_id = settings.AWS_ACCESS_KEY_ID
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
            region_name = settings.AWS_REGION

            s3_client = boto3.client(service_name="s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

            for i in range(len(target_list)):
                obj = s3_client.get_object(Bucket="subprice", Key="static/csv/" + target_list[i])
                data_list.append(pd.read_csv(io.BytesIO(obj["Body"].read())))
        
        # Type 모델 데이터
        for row in data_list[0].itertuples():
            try:
                Type.objects.get_or_create(id=row[1], method_type=row[2])
            except:
                continue
        
        # Company 모델 데이터    
        for row in data_list[1].itertuples():
            try:
                Company.objects.get_or_create(id=row[1], company=row[2])
            except:
                continue
            
        # Category 모델 데이터    
        for row in data_list[2].itertuples():
            try:
                Category.objects.get_or_create(id=row[1], category_type=row[2])
            except:
                continue
            
        # Service 모델 데이터    
        for row in data_list[3].itertuples():
            try:
                Service.objects.get_or_create(id=row[1], name=row[2], category_id=row[3])
            except:
                continue
            
        # Plan 모델 데이터    
        for row in data_list[4].itertuples():
            try:
                Plan.objects.get_or_create(id=row[1], name=row[2], price=row[3], service_id=row[4])
            except:
                continue