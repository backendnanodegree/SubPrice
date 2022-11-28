from django.db import models
from users.models import BaseModel
from subscriptions.models import Subscription


class Alarm(BaseModel):
    NO = -1
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    DDAY_TYPE = [
        (NO, "미설정"),
        (ONE, "1일전"),
        (TWO, "2일전"),
        (THREE, "3일전"),
        (FOUR, "4일전"),
        (FIVE, "5일전"),
        (SIX, "6일전"),
        (SEVEN, "7일전"),
    ]
    d_day = models.SmallIntegerField(verbose_name="메일발송 D-DAY", choices=DDAY_TYPE, help_text="선택 시, 해당 일자에 메일이 발송됩니다.", null=True)
    subscription = models.OneToOneField(Subscription, verbose_name="구독정보", on_delete=models.CASCADE, null=True, related_name="alarm_subscription")

    def __str__(self):
        return f"({self.subscription})의 {self.get_d_day_display()} 알림"

    class Meta:
        verbose_name = "알림 정보"
        verbose_name_plural = "알림 정보 목록"

class AlarmHistory(BaseModel):
    alarm = models.ForeignKey(Alarm, verbose_name='알림', on_delete=models.CASCADE, null=True)
    content = models.TextField(verbose_name='알림 내역', default='', null=True, blank=True, help_text='발송시 메일 내용을 그대로 넣어줍니다.')
    
    def __str__(self):
        return f"({self.alarm}) 내역"

    class Meta:
        verbose_name = "알림 내역"
        verbose_name_plural = "알림 내역 목록"
