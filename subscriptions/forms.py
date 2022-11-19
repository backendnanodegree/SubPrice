from django import forms
from django.forms import NumberInput
from django.forms import ValidationError
import calendar

from subscriptions.models import Plan, Service


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
        started_at = cleaned_data.get("started_at")
        expire_at = cleaned_data.get("expire_at")
        
        error = {}

        # plan validation
        plan_list = [ plan[0] for plan in Service.objects.get(name=service).plan_service.values_list("name") ]
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
                
        if error:
            raise ValidationError(error)

        return cleaned_data


class SubscriptionUpdateForm(forms.Form):

    
    METHOD_TYPE = [(1, "신용카드"), (2, "체크카드"), (3, "계좌이체"), (4, "간편결제"), (5, "휴대폰결제")]
    DDAY_TYPE = [(-1, '미설정'), (1, '1일전'), (2, '2일전'), (3, '3일전'), (4, '4일전'), (5, '5일전'), (6, '6일전'), (7, '7일전')]

    service_name = forms.CharField(label="서비스", widget=forms.TextInput())
    plan_name = forms.CharField(label="서비스 유형", widget=forms.TextInput())
    started_at = forms.DateTimeField(label="구독시작일", widget=NumberInput(attrs={'type':'date'}))
    expire_at = forms.DateTimeField(label="만료예정일", widget=NumberInput(attrs={'type':'date'}), required=False)
    company = forms.CharField(label="결제사", widget=forms.TextInput())
    method_type = forms.ChoiceField(label="결제수단", widget=forms.Select, choices=METHOD_TYPE)
    d_day = forms.ChoiceField(label="알람설정", widget=forms.Select, choices=DDAY_TYPE)

    def clean(self):

        cleaned_data = super(SubscriptionUpdateForm, self).clean()

        started_at = cleaned_data.get("started_at")
        expire_at = cleaned_data.get("expire_at")    

        if expire_at:
            sub_last_day = calendar.monthrange(int(started_at.strftime("%Y")), int(started_at.strftime("%m")))[1]
            exp_last_day = calendar.monthrange(int(expire_at.strftime("%Y")), int(expire_at.strftime("%m")))[1]
            
            expire_at_error1 = started_at.strftime("%Y%m") >= expire_at.strftime("%Y%m")
            expire_at_error2 = started_at.strftime("%d") != sub_last_day and started_at.strftime("%d") != expire_at.strftime("%d")
            expire_at_error3 = int(started_at.strftime("%d")) == sub_last_day and int(expire_at.strftime("%d")) == exp_last_day and sub_last_day >= exp_last_day

            if (expire_at_error1) or (expire_at_error2):
                if expire_at_error3:
                    pass
                else:
                    raise ValidationError({"expire_at":["만료예정일을 확인해주세요."]})

        return cleaned_data