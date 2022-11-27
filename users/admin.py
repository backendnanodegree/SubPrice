from django.contrib import admin
from django.utils.html import format_html
from django.core.checks import messages
from django.conf import settings

from users.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "fullname", "phone", "is_active", "is_admin", "get_picture"]
    search_fields = ["email", "fullname", "phone", "is_active"]
    actions = ["activate_change"]
    
    @admin.display(description="프로필 사진")
    def get_picture(self, obj):
        if obj.picture:
            return format_html(f'<img src="{obj.picture.url}" alt="프로필 사진" style="width:30px; height:20px;">')
        else:
            try:
                return format_html(f'<img src="{settings.S3_STATIC_URL+"img/profile.png"}" alt="프로필 사진" style="width:20px; height:20px;">')
            except:
                return format_html(f'<img src="{settings.STATIC_URL+"img/profile.png"}" alt="프로필 사진" style="width:20px; height:20px;">')

    @admin.display(description="사용자 활성 여부 변경")
    def activate_change(self, request, queryset):
        queryset = queryset.filter(is_admin=False)
        activate_cnt = 0
        deactivate_cnt = 0

        for item in queryset:
            # 유저 활성 여부 변경
            active_status = item.is_active
            item.is_active = 1-active_status
            item.save()
            # 해당 유저의 구독 정보 삭제/사용 처리
            subscription_list = item.subscription_user.all()

            if active_status == 1:
                activate_cnt += 1
                subscription_list.update(delete_on=False)
            else:
                deactivate_cnt += 1
                subscription_list.update(delete_on=True)

        if activate_cnt and deactivate_cnt:
            message = f"{activate_cnt} 명의 계정을 비활성화 / {deactivate_cnt} 명의 계정을 활성화 하였습니다."
        elif activate_cnt:
            message = f"{activate_cnt} 명의 계정을 비활성화 하였습니다."
        elif deactivate_cnt:
            message = f"{deactivate_cnt} 명의 계정을 활성화 하였습니다."

        self.message_user(request, message, level=messages.INFO)