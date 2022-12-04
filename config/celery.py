import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# 셀러리를 장고에서 사용하기위한 환경설정 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Celery 객체 생성 후 app 변수로 선언
# 객체 내부에 상세설정은 settings.py에도 설정해두었지만 여기서 명시적으로 작성
# 추후 삭제 or 수정 예정
app = Celery('config',
             # 브로커로 레디스를 사용
             broker= 'redis://redis:6379',
             # 셀러리의 작업내용을 django-db에 자동으로 저장(admin에서 볼 수 있음)
             backend= 'django-db',
             # config 앱의 tasts.py에 있는 작업들을 수행하도록 설정
             include=['config.tasks'])

# settings.py 맨 아래부분에 직접 설정해둔 celery 관련 환경설정을 적용
app.config_from_object('django.conf:settings', namespace='CELERY')

# 셀러리가 tasks.py에 작성된 작업을 어떻게 서버와 주고받을지 결정
# 이 설정도 settings.py에 작성해두었으며 추후 수정 예정
app.conf.update(
    task_serializer='json',
    accept_content=['application/json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=False,
)

# 장고 프로젝트 실행 시 아래 스케줄링 작업을 자동으로 등록
app.conf.beat_schedule = {
    # 이 key 값은 admin 페이지에서 보여지는 이름 (수정가능)
    'send_mail_to_client_every9am': {
        # tasks.py 에 선언해둔 send_mail_task를 실행
        'task': 'config.tasks.send_mail_task',
        # 매일 오전 9시
        'schedule': crontab(hour=9, minute=0),
        },
    # 매일 자정마다 만료구독정보 갱신
    'check_expired_subscriptions_everyday': {
        'task': 'config.tasks.check_expired_task',
        # 매일 자정 00시 01분
        'schedule': crontab(hour=0, minute=1),
    }
}

# 앱에서 @shared_task 데코레이터를 붙여둔 함수들을 찾아서 자동으로 셀러리에게 등록
app.autodiscover_tasks() 

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
