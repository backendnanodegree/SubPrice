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

        # AMAZON S3 경로 지정
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        region_name = settings.AWS_REGION

        s3_client = boto3.client(service_name="s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
        
        # Type 모델 데이터
        obj = s3_client.get_object(Bucket="subprice", Key="static/csv/type.csv")
        data = pd.read_csv(io.BytesIO(obj["Body"].read()))

        for row in data.itertuples():
            try:
                Type.objects.get_or_create(id=row[1], method_type=row[2])
            except:
                continue
        
        # Company 모델 데이터    
        obj = s3_client.get_object(Bucket="subprice", Key="static/csv/company.csv")
        data = pd.read_csv(io.BytesIO(obj["Body"].read()))
        
        for row in data.itertuples():
            try:
                Company.objects.get_or_create(id=row[1], company=row[2])
            except:
                continue
            
        # Category 모델 데이터    
        obj = s3_client.get_object(Bucket="subprice", Key="static/csv/category.csv")
        data = pd.read_csv(io.BytesIO(obj["Body"].read()))
        
        for row in data.itertuples():
            try:
                Category.objects.get_or_create(id=row[1], category_type=row[2])
            except:
                continue
            
        # Service 모델 데이터    
        obj = s3_client.get_object(Bucket="subprice", Key="static/csv/service.csv")
        data = pd.read_csv(io.BytesIO(obj["Body"].read()))
        
        for row in data.itertuples():
            try:
                Service.objects.get_or_create(id=row[1], name=row[2], category_id=row[3])
            except:
                continue
            
        # Plan 모델 데이터    
        obj = s3_client.get_object(Bucket="subprice", Key="static/csv/plan.csv")
        data = pd.read_csv(io.BytesIO(obj["Body"].read()))
        
        for row in data.itertuples():
            try:
                Plan.objects.get_or_create(id=row[1], name=row[2], price=row[3], service_id=row[4])
            except:
                continue