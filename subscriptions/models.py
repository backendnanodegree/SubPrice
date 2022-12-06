from django.db import models
from users.models import BaseModel, User

from datetime import datetime
from dateutil.relativedelta import relativedelta

# Create your models here.


class Type(BaseModel):
    DEFAULT = 0
    CREDIT = 1
    CHECK = 2
    ACCOUNT = 3
    EASY = 4
    MOBILE = 5
    METHOD_TYPE = [
        (DEFAULT, "-- 선택 --"),
        (CREDIT, "신용카드"),
        (CHECK, "체크카드"),
        (ACCOUNT, "계좌이체"),
        (EASY, "간편결제"),
        (MOBILE, "휴대폰결제"),
    ]
    method_type = models.PositiveSmallIntegerField(verbose_name="결제유형", choices=METHOD_TYPE, unique=True)
    company = models.ManyToManyField("subscriptions.Company", through="Billing", verbose_name="결제사", related_name="type_company")

    def __str__(self):
        return self.get_method_type_display()

    class Meta:
        verbose_name = "결제유형"
        verbose_name_plural = "결제유형 목록"


class Company(BaseModel):
    type = models.ManyToManyField("subscriptions.Type", through="Billing", verbose_name="결제수단", related_name="company_type")
    company = models.CharField(verbose_name="결제사", max_length=50)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = "결제사"
        verbose_name_plural = "결제사 목록"


class Billing(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="사용자", related_name="type_user")
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name="결제수단", related_name="billing_type")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="결제사", related_name="billing_company")

    def __str__(self):
        return f"{self.company} - {self.type}"

    class Meta:
        verbose_name = "결제수단"
        verbose_name_plural = "결제수단 목록"


class Category(BaseModel):
    DEFAULT = 0
    OTT = 1
    MUSIC = 2
    BOOK = 3
    DISTRIBUTION = 4
    SOFTWARE = 5
    DELIEVERY = 6
    RENTAL = 7
    CATEGORY_TYPE = [
        (DEFAULT, "-- 선택 --"),
        (OTT, "OTT"),
        (MUSIC, "음악"),
        (BOOK, "도서"),
        (DISTRIBUTION, "유통"),
        (SOFTWARE, "소프트웨어"),
        (DELIEVERY, "정기배송"),
        (RENTAL, "렌탈"),
    ]
    category_type = models.PositiveSmallIntegerField(verbose_name="카테고리 종류", choices=CATEGORY_TYPE, unique=True)

    def __str__(self):
        return self.get_category_type_display()

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리 목록"


class Service(BaseModel):
    category = models.ForeignKey(Category, verbose_name="서비스", on_delete=models.CASCADE, related_name="service_category")
    name = models.CharField(verbose_name="서비스명", max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "서비스"
        verbose_name_plural = "서비스 목록"


class Plan(BaseModel):
    service = models.ForeignKey(Service, verbose_name="서비스", on_delete=models.CASCADE, related_name="plan_service")
    name = models.CharField(verbose_name="구독플랜", max_length=50)
    price = models.PositiveIntegerField(verbose_name="가격")

    def __str__(self):
        return f"{self.service} - {self.name}"

    class Meta:
        verbose_name = "구독 플랜"
        verbose_name_plural = "구독 플랜 목록"


class Subscription(BaseModel):
    user = models.ForeignKey("users.User", verbose_name="사용자", on_delete=models.CASCADE, null=True, related_name="subscription_user")
    plan = models.ForeignKey(Plan, verbose_name="구독플랜", on_delete=models.CASCADE, null=True, related_name="subscription_plan")
    billing = models.ForeignKey(Billing, verbose_name="결제 정보", on_delete=models.CASCADE, null=True, related_name="subscription_billing")
    started_at = models.DateField(verbose_name="최초 구독일")
    expire_at = models.DateField(verbose_name="구독 만료일", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="활성 여부", default=True)
    delete_on = models.BooleanField(verbose_name="삭제 여부", default=False)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    def next_billing_at(self):

        if self.is_active == 0:
            return None

        # 매 월의 마지막 일자
        last_day_list = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

        # 오늘 일자
        now = datetime.now().date()

        # 구독 시작일
        started_day = self.started_at.day

        # 기준 월 계산
        the_month = now if started_day >= now.day else now + relativedelta(months=1)
        the_month_last_day = 29 if the_month.year % 4 == 0 and the_month.month == 2 else last_day_list[the_month.month]

        # 일 계산
        the_day = started_day if started_day <= the_month_last_day else the_month_last_day

        # 해당 월의 해당 일자 출력
        return the_month.replace(day=the_day)

    class Meta:
        verbose_name = "사용자 구독 정보"
        verbose_name_plural = "사용자 구독 정보 목록"