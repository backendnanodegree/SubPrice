from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from subscriptions.models import Subscription
from alarms.models import Alarm, AlarmHistory
import datetime

@shared_task
def send_mail_task():
    # 함수가 제대로 실행되었는지 확인하기위해 터미널에 프린트문 출력
    print("Mail sending...")

    # settings에 설정해둔 email_host_user(batmantwo7233@gmail.com)을 발신자로 설정
    email_from = settings.EMAIL_HOST_USER

    # 오늘날짜
    today = datetime.date.today()

    # 유저가 알람여부를 선택한 알람쿼리셋 호출
    alarm_sub_queryset = Alarm.objects.exclude(d_day= -1)

    # 알람이 설정된 각각의 쿼리를 조회
    for need_alarm_sub in alarm_sub_queryset:
        # 구독 만료일
        expired_day = need_alarm_sub.subscription.expire_at

        # 만료일이 입력되지 않은경우 패스
        if expired_day == None:
            continue

        # 만료일이 설정된 유저의 d_day (n일 전)
        dday = int(need_alarm_sub.d_day)

        # 만료일에서 dday를 뺀 알람발송 목표일
        target_day = expired_day - datetime.timedelta(days=dday)

        # 메일발송 목표일이 오늘인경우 메일 발송
        if target_day == today:
            # 오늘 메일을 보내야하는 구독정보
            target_sub = need_alarm_sub.subscription

            # 구독정보의 데이터를 이용해서 send_mail의 파라미터로 넣어서 메일발송
            # 메일을 받는 유저의 이메일을 리스트안엔 넣음 (하나인데 리스트인 이유는 send_mail함수가 이 값을 리스트로 받아야함)
            recipient_list = [target_sub.user.email]
            # 이메일 제목 설정
            subject = f'{target_sub.user.fullname}님의 구독결제 예정 알람메일 입니다.'
            # 이메일 내용 설정
            message = f'안녕하세요, SubPrice 입니다. 회원님의 {target_sub.plan.service.name} - {target_sub.plan.name} / {target_sub.plan.price}원이 {expired_day}에 결제 >예정입니다.'
            # 메일발송 함수(장고 코어의 내장함수)
            send_mail(subject, message, email_from, recipient_list)

            # 메일을 보냈다면 보낸 내용을 alarmhistory에 데이터 저장
            history = AlarmHistory.objects.create(alarm=need_alarm_sub, content=message, is_success=True, traceback = '')
            history.save()

    # 리턴문은 터미널에서 작업이 완료되었는지 확인하기위해 작성        
    return "Mail has been sent..."


# 구독정보가 만료되었는지 확인하는 함수
@shared_task
def check_expired_task():
    print("Check subscription list...")

    # 어제가 구독 만료일이었던 구독정보 쿼리셋을 가져옴
    # 어제날짜 선언
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    # 구독 만료일이 어제였던 (오늘 만료된) 쿼리셋 호출
    expired_subs = Subscription.objects.filter(expire_at=yesterday)

    # 만료된 각각의 구독정보 테이블의 is_active = 0 으로 변경 후 저장
    for sub in expired_subs:
        sub.is_active = 0
        sub.save()