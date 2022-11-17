from users.models import User
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from random import *

# TODO: 커맨드 활용
# https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/#testing
class Command(BaseCommand):
    help = "PUSH USER DB"

    def handle(self, *args, **options):
        
        # 생성할 user 수
        number = int(input("생성할 user의 수를 입력하세요 : "))
        
        
        # email_list
        english_characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 
                            'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        domain_type = ['naver.com', 'google.com', 'kakao.com', 'hanmail.net', 'daum.net', 
                       'nate.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'yahoo.com' ]
        domains = choices(domain_type, weights=[40, 15, 10, 15, 10, 10, 3 ,2, 15, 5], k=number)
        id_sizes = choices(list(range(5,11)), k=number)

        email_list = [''.join(choices(english_characters,k=id_length))+"@"+domain for id_length, domain in zip(id_sizes, domains)]


        # fullname_list
        lastname_type = ["김","이","박","최","정","강","조","윤","장","임","오","한","신","서","권"]
        korean_characters = ["가","나","다","라","마","바","사","아","자","차","카","타","파","하",
                            "고","노","도","로","모","보","소","오","조","초","코","토","포","호"]
        lastname_list = choices(lastname_type, k=number)
        name_sizes = choices([1,2],weights=[1,50], k=number)
        fullname_list = [lastname+''.join(choices(korean_characters,k=name_length)) for lastname, name_length in zip(lastname_list, name_sizes)]
        
        
        # phone_list
        middle_numbers = list(map(str, list(range(20,59)) + list(range(62, 100))))
        numbers = ['0','1','2','3','4','5','6','7','8','9']
        phone_list = ['010'+ choice(middle_numbers) + ''.join(choices(numbers,k=6)) for _ in range(number)]
        
        # password
        new_password = make_password('1234')
        
        # Create User objects
        for email, fullname, phone in zip(email_list, fullname_list, phone_list):
            User.objects.get_or_create(email=email, fullname=fullname, password=new_password, phone=phone)
