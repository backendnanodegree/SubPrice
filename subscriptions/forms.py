from django import forms
from django.forms import NumberInput
from django.forms import ValidationError
import calendar

from subscriptions.models import Service, Company, Plan


class SubscriptionForm(forms.Form):
    
    METHOD_TYPE = [(1, "신용카드"), (2, "체크카드"), (3, "계좌이체"), (4, "간편결제"), (5, "휴대폰결제")]
    DDAY_TYPE = [(-1, '미지정'), (1, '1일전'), (2, '2일전'), (3, '3일전'), (4, '4일전'), (5, '5일전'), (6, '6일전'), (7, '7일전')]

    category = forms.CharField(label="카테고리", widget=forms.TextInput(attrs={'readonly':True}), required=False)
    service = forms.CharField(label="서비스", widget=forms.TextInput())
    plan = forms.CharField(label="서비스 유형", widget=forms.TextInput())
    started_at = forms.DateTimeField(label="구독시작일", widget=NumberInput(attrs={'type':'date'}))
    expire_at = forms.DateTimeField(label="만료예정일", widget=NumberInput(attrs={'type':'date'}), required=False)
    price = forms.CharField(label="결제금액", widget=forms.TextInput(attrs={'readonly':True}), required=False)
    company = forms.CharField(label="결제사", widget=forms.TextInput())
    type_object = forms.ChoiceField(label="결제수단", widget=forms.Select, choices=METHOD_TYPE)
    alarm = forms.ChoiceField(label="알람설정", widget=forms.Select, choices=DDAY_TYPE)

    def clean(self):

        cleaned_data = super(SubscriptionForm, self).clean()

        service = cleaned_data.get("service")
        plan = cleaned_data.get("plan")
        method_type = cleaned_data.get("method_type")
        company = cleaned_data.get("company")
        started_at = cleaned_data.get("started_at")
        expire_at = cleaned_data.get("expire_at")
        
        error = {}

        # plan validation
        plan_list = Service.objects.get(name=service).plan_service.values_list("name", flat=True)
        if plan not in plan_list:
            error['plan'] = ["서비스에 해당 서비스 유형이 존재하지 않습니다."]

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
        company_list = Company.objects.values_list('company', flat=True)
        credit_card = company_list[19:38]
        check_card = company_list[19:37]
        account = company_list[0:19]
        easy_payment = company_list[38:52]
        mobile_payment = list(company_list[45:46]) + list(company_list[52:57])
        error_company_message = ["결제유형에 해당 결제사가 존재하지 않습니다."]

        # 결제 유형이 '신용카드'인 경우 → '신용카드'에 해당하는 결제사가 아니라면 에러 발생
        if method_type == '1':
            if company not in credit_card:
                error['company'] = error_company_message
        # 결제 유형이 '체크카드'인 경우 → '체크카드'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '2':
            if company not in check_card:
                error['company'] = error_company_message
        # 결제 유형이 '계좌이체'인 경우 → '계좌이체'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '3':
            if company not in account:
                error['company'] = error_company_message
        # 결제 유형이 '간편결제'인 경우 → '간편결제'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '4':
            if company not in easy_payment:
                error['company'] = error_company_message
        # 결제 유형이 '휴대폰결제'인 경우 → '휴대폰결제'에 해당하는 결제사가 아니라면 에러 발생
        elif method_type == '5':
            if company not in mobile_payment:
                error['company'] = error_company_message
        if error:
            raise ValidationError(error)

        return cleaned_data


class SubscriptionUpdateForm(forms.Form):

    
    METHOD_TYPE = [(1, "신용카드"), (2, "체크카드"), (3, "계좌이체"), (4, "간편결제"), (5, "휴대폰결제")]
    DDAY_TYPE = [(-1, '미설정'), (1, '1일전'), (2, '2일전'), (3, '3일전'), (4, '4일전'), (5, '5일전'), (6, '6일전'), (7, '7일전')]

    service_list = sorted(Service.objects.all().values_list('id', 'name'))
    plan_list = sorted(Plan.objects.all().values_list('id', 'name'))
    company_list = sorted(Company.objects.all().values_list('id', 'company'))

    service_type = forms.ChoiceField(label="서비스", widget=forms.Select, choices=service_list)
    plan_type = forms.ChoiceField(label="서비스 유형", widget=forms.Select, choices=plan_list)
    started_at = forms.DateTimeField(label="구독시작일", widget=NumberInput(attrs={'type':'date'}))
    expire_at = forms.DateTimeField(label="만료예정일", widget=NumberInput(attrs={'type':'date'}), required=False)
    method_type = forms.ChoiceField(label="결제수단", widget=forms.Select, choices=METHOD_TYPE)
    company_type = forms.ChoiceField(label="결제사", widget=forms.Select, choices=company_list)
    d_day = forms.ChoiceField(label="알람설정", widget=forms.Select, choices=DDAY_TYPE)

    def clean(self):

        cleaned_data = super(SubscriptionUpdateForm, self).clean()

        service_type = cleaned_data.get("service_type")
        plan_type = int(cleaned_data.get("plan_type"))
        method_type = cleaned_data.get("method_type")
        company_type = int(cleaned_data.get("company_type"))
        started_at = cleaned_data.get("started_at")
        expire_at = cleaned_data.get("expire_at")
 
        error = {}

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
        credit_card = list(range(20,39))
        check_card = list(range(20,38))
        account = list(range(1,20))
        easy_payment = list(range(39,53))
        mobile_payment = [46] + list(range(53,58))
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