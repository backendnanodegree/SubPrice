import re

from django import forms
from users.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class LoginForm(forms.Form):
    """
    최선우 : forms.Form을 상속받아 로그인 입력 폼 생성.
            - clean 함수를 통한 검증 진행
    """
    email = forms.EmailField(label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"}))
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={"placeholder": "비밀번호", "autocomplete": "new-password"}))

    
    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        user = User.objects.filter(email=email).last()

        if not user:
            raise ValidationError({"email": "올바른 이메일 주소를 입력해주세요."})

        elif not check_password(password, user.password):
            raise ValidationError({"password": "잘못된 비밀번호입니다. 다시 확인하세요."})

        return cleaned_data