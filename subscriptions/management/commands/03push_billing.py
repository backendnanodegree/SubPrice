
from subscriptions.models import Billing
from users.models import User
from django.core.management.base import BaseCommand
from random import *

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH BILLING DB"

    def handle(self, *args, **options):
        
    # 각 유저별 5개씩의 결제수단 등록
        
        # 결제유형, 결제사 id 리스트
        pay_type = list(map(str, list(range(2,7))))
        pay_company = list(map(str, list(range(2,59))))
        
        
        # 결제유형별 등록 가능한 결제사 id 리스트
        credit_card = pay_company[19:38]
        check_card = pay_company[19:37]
        account = pay_company[1:20]
        easy_payment = pay_company[38:52]
        mobile_payment = pay_company[52:57]
        
        
        # 결제유형 및 결제사 id 랜덤 추출
        def get_company_id(type_id):
            if type_id == '2':
                company_id = choice(credit_card)
            elif type_id == '3':
                company_id = choice(check_card)
            elif type_id == '4':
                company_id = choice(account)
            elif type_id == '5':
                company_id = choice(easy_payment)
            elif type_id == '6':
                company_id = choice(mobile_payment)
            return company_id
        
        # 전체 유저 불러오기
        users = User.objects.all()
        length = len(users)
        
        # 각 유저별로 5개 씩의 결제수단 등록
        for i in range(length):
            cnt = 0
            while cnt < 5:
                user_id = users[i].id
                type_id = choice(pay_type)
                company_id = get_company_id(type_id)
                
                billing_object, is_created = Billing.objects.get_or_create( \
                                    company_id=company_id, type_id=type_id, user_id=user_id)
                if is_created == True:
                    cnt += 1
                
        