import csv
import pandas as pd
import boto3
import io
from django.conf import settings

from django import forms
from django.forms import NumberInput
from django.forms import ValidationError
import calendar

from subscriptions.models import Service, Company, Plan

class MyBaseForm(forms.Form):

    # csv 파일로부터 company, service, plan 리스트를 불러와 아래에서 생성할 폼에 사용하기 위해 부모 클래스 폼을 생성
    # - csv 파일 읽어오는 'static' 경로 : config/settings.py에서 설정

    target_list = ["company.csv", "service.csv", "plan.csv"]
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

        for i in range(3):
            obj = s3_client.get_object(Bucket="subprice", Key="static/csv/" + target_list[i])
            data_list.append(pd.read_csv(io.BytesIO(obj["Body"].read())))

    company_data, service_data, plan_data = data_list[0], data_list[1], data_list[2]

    company_list = company_data.to_records(index=False).tolist()
    service_list = service_data.iloc[:,[0,1]].to_records(index=False).tolist()
    plan_list = plan_data.iloc[:,[0,1]].to_records(index=False).tolist()

    class Meta:
        abstract = True

class SubscriptionForm(MyBaseForm):
    
    CATEGORY_TYPE = [(0, "-- 선택 --"),(1, "OTT"),(2, "음악"),(3, "도서"),(4, "유통"),(5, "소프트웨어"),(6, "정기배송"),(7, "렌탈")]
    METHOD_TYPE = [(0, "-- 선택 --"),(1, "신용카드"), (2, "체크카드"), (3, "계좌이체"), (4, "간편결제"), (5, "휴대폰결제")]
    DDAY_TYPE = [(-1, '미설정'), (1, '1일전'), (2, '2일전'), (3, '3일전'), (4, '4일전'), (5, '5일전'), (6, '6일전'), (7, '7일전')]

    category_type = forms.ChoiceField(label="카테고리", widget=forms.Select, choices=CATEGORY_TYPE)
    service_type = forms.ChoiceField(label="서비스", widget=forms.Select, choices=MyBaseForm().service_list)
    plan_type = forms.ChoiceField(label="서비스 유형", widget=forms.Select, choices=MyBaseForm().plan_list)
    started_at = forms.DateTimeField(label="구독시작일", widget=NumberInput(attrs={'type':'date'}))
    expire_at = forms.DateTimeField(label="만료예정일", widget=NumberInput(attrs={'type':'date'}), required=False)
    price = forms.CharField(label="결제금액", widget=forms.TextInput(attrs={'id':'id_price'}), disabled=True, required=False)
    method_type = forms.ChoiceField(label="결제수단", widget=forms.Select, choices=METHOD_TYPE)
    company_type = forms.ChoiceField(label="결제사", widget=forms.Select, choices=MyBaseForm().company_list)
    d_day = forms.ChoiceField(label="알람설정", widget=forms.Select, choices=DDAY_TYPE)

    def clean(self):

        cleaned_data = super(SubscriptionForm, self).clean()

        category_type = cleaned_data.get("category_type")
        service_type = cleaned_data.get("service_type")
        plan_type = int(cleaned_data.get("plan_type"))
        method_type = cleaned_data.get("method_type")
        company_type = int(cleaned_data.get("company_type"))
        started_at = cleaned_data.get("started_at")
        expire_at = cleaned_data.get("expire_at")
 
        error = {}

        # choice validation
        if category_type == 0 or service_type == 1 or plan_type ==1 or method_type == 0 or company_type == 1:
            error['category_type'] = ["각 항목에 맞는 데이터를 바르게 선택해주세요."]

        # plan validation
        plan_list = Service.objects.get(id=service_type).plan_service.values_list("id", flat=True)
        if plan_type not in plan_list:
            error['plan_type'] = ["서비스에 해당 서비스 유형이 존재하지 않습니다."]

        # expire_at validation
        if expire_at:
            sub_last_day = calendar.monthrange(int(started_at.strftime("%Y")), int(started_at.strftime("%m")))[1]
            exp_last_day = calendar.monthrange(int(expire_at.strftime("%Y")), int(expire_at.strftime("%m")))[1]

            expire_at_error1 = started_at.strftime("%Y%m") >= expire_at.strftime("%Y%m")
            expire_at_error2 = int(started_at.strftime("%d")) != sub_last_day and started_at.strftime("%d") != expire_at.strftime("%d")
            expire_at_error3 = int(started_at.strftime("%d")) == sub_last_day and int(expire_at.strftime("%d")) != exp_last_day and sub_last_day != int(expire_at.strftime("%d"))
            expire_at_error4 = int(started_at.strftime("%d")) == sub_last_day and int(expire_at.strftime("%d")) == exp_last_day and sub_last_day < exp_last_day
  
            if (expire_at_error1) or (expire_at_error2) or (expire_at_error3) or (expire_at_error4):
                error['expire_at'] = ["만료예정일이 올바른 일자가 아닙니다."]

        # billing validation
        credit_card = list(range(21,40))
        check_card = list(range(21,39))
        account = list(range(2,21))
        easy_payment = list(range(40,54))
        mobile_payment = [47] + list(range(54,59))
        error_company_message = ["결제유형에 해당 결제사가 존재하지 않습니다."]

        # 결제 유형이 '신용카드'인 경우 → '신용카드'에 해당하는 결제사가 아니라면 에러 발생
        if method_type == '1':
            if company_type not in credit_card:
                error['company_type'] = error_company_message
        # 결제 유형이 '체크카드'인 경우 → '체크카드'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '2':
            if company_type not in check_card:
                error['company_type'] = error_company_message
        # 결제 유형이 '계좌이체'인 경우 → '계좌이체'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '3':
            if company_type not in account:
                error['company_type'] = error_company_message
        # 결제 유형이 '간편결제'인 경우 → '간편결제'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '4':
            if company_type not in easy_payment:
                error['company_type'] = error_company_message
        # 결제 유형이 '휴대폰결제'인 경우 → '휴대폰결제'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '5':
            if company_type not in mobile_payment:
                error['company_type'] = error_company_message
        if error:
            raise ValidationError(error)

        return cleaned_data