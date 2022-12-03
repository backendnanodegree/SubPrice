from .celery import app as celery_app

# 앱이 실행되면 task.py에 만들어놓은 스케쥴링 작업용 함수를 자동으로 찾아서 등록
__all__ = ('celery_app',)