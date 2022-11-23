from django.contrib import admin
from django.utils.html import format_html
from django.core.checks import messages

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
            return format_html(f'<img src="/static/img/profile.png" alt="프로필 사진" style="width:20px; height:20px;">')

    @admin.display(description="사용자 활성 여부 변경")
    def activate_change(self, request, queryset):
        queryset = queryset.filter(is_admin=False)
        activate_cnt = 0
        deactivate_cnt = 0

        for item in queryset:
            active_status = item.is_active
            item.is_active = 1-active_status
            item.save()
            if active_status == 1:
                activate_cnt += 1
            else:
                deactivate_cnt += 1

        if activate_cnt and deactivate_cnt:
            message = f"{activate_cnt} 명의 계정을 비활성화 / {deactivate_cnt} 명의 계정을 활성화 하였습니다."
        elif activate_cnt:
            message = f"{activate_cnt} 명의 계정을 비활성화 하였습니다."
        elif deactivate_cnt:
            message = f"{deactivate_cnt} 명의 계정을 활성화 하였습니다."

        self.message_user(request, message, level=messages.INFO)