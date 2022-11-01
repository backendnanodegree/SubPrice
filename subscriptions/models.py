from django.db import models
from users.models import Baseclass, User

# Create your models here.

class Type(Baseclass):
    """
    최선우 : 결제유형 모델 생성 -> 관리자가 데이터 관리 예정
    """
    CREDIT = 1
    CHECK = 2
    ACCOUNT = 3
    EASY = 4
    MOBILE = 5
    METHOD_TYPE = [
        (CREDIT, '신용카드'), (CHECK, '체크카드'),
        (ACCOUNT, '계좌이체'), (EASY, '간편결제'), (MOBILE, '휴대폰결제'),
    ]
    method_type = models.PositiveSmallIntegerField(verbose_name='결제유형', choices=METHOD_TYPE, unique=True)
    company = models.ManyToManyField('subscriptions.Company', through='Billing', verbose_name="결제사", related_name="type_company")
    
    def __str__(self):
        return self.get_method_type_display()

    class Meta:
        verbose_name = '결제유형'
        verbose_name_plural = "결제유형 목록"

class Company(Baseclass):
    """
    최선우 : 결제사 모델 생성 -> 관리자가 데이터 관리 예정
    """
    type = models.ManyToManyField('subscriptions.Type', through='Billing', verbose_name="결제수단", related_name="company_type")
    company = models.CharField(verbose_name='결제사', max_length=50)
    
    def __str__(self):
        return self.company

    class Meta:
        verbose_name = '결제사'
        verbose_name_plural = "결제사 목록"
        
class Billing(Baseclass):
    """
    최선우 : 결제수단 모델 생성 -> 관리자가 데이터 관리 예정
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='사용자', related_name="type_user")
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name="결제수단", related_name="billing_type")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="결제사", related_name="billing_company")

    def __str__(self):
        return f"{self.company} - {self.type}"

    class Meta:
        verbose_name = '결제수단'
        verbose_name_plural = "결제수단 목록"

    
class Category(Baseclass):
    """
    최선우 : 카테고리 모델 생성 -> 관리자가 데이터 관리 예정
    """
    OTT = 1
    MUSIC = 2
    BOOK = 3
    DISTRIBUTION = 4
    SOFTWARE = 5
    DELIEVERY = 6
    RENTAL = 7
    CATEGORY_TYPE = [
        (OTT, 'OTT'), (MUSIC, '음악'), (BOOK, '도서'), (DISTRIBUTION, '유통'),
        (SOFTWARE, '소프트웨어'), (DELIEVERY, '정기배송'), (RENTAL, '렌탈'),
    ]
    category_type = models.PositiveSmallIntegerField(verbose_name='카테고리 종류', choices=CATEGORY_TYPE, unique=True)

    def __str__(self):
        return self.get_category_type_display()
    
    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = "카테고리 목록"
        
class Service(Baseclass):
    """
    최선우 : 서비스 모델 생성 -> 관리자가 데이터 관리 예정
    """
    category = models.ForeignKey(Category, verbose_name='서비스', on_delete=models.PROTECT, related_name='service_category')
    name = models.CharField(verbose_name='서비스명', max_length=50, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '서비스'
        verbose_name_plural = "서비스 목록"
        
class Plan(Baseclass):
    """
    최선우 : 플랜 모델 생성 -> 관리자가 데이터 관리 예정
    """
    service = models.ForeignKey(Service, verbose_name='서비스', on_delete=models.CASCADE, related_name='plan_service')
    name = models.CharField(verbose_name='구독플랜', max_length=50)
    price = models.PositiveIntegerField(verbose_name='가격')

    def __str__(self):
        return f"{self.service} - {self.name}"

    class Meta:
        verbose_name = '구독 플랜'
        verbose_name_plural = "구독 플랜 목록"


class Subscription(Baseclass):
    """
    최선우 : 구독 정보 모델 생성 -> 유저가 직접 등록
    """
    user = models.ForeignKey('users.User', verbose_name='사용자', on_delete=models.SET_NULL, null=True, related_name='subscription_user')
    plan = models.ForeignKey(Plan, verbose_name='구독플랜', on_delete=models.SET_NULL, null=True, related_name='subscription_plan')
    billing = models.ForeignKey(Billing, verbose_name='결제 정보', on_delete=models.SET_NULL, null=True, related_name='subscription_billing')
    started_at = models.DateField(verbose_name='최초 구독일')
    expire_at = models.DateField(verbose_name='구독 만료일', null=True, blank=True)
    is_active = models.BooleanField(verbose_name="활성 여부", default=True)
    
    def __str__(self):
        return f"{self.user} - {self.plan}"

    class Meta:
        verbose_name = '사용자 구독 정보'
        verbose_name_plural = "사용자 구독 정보 목록"