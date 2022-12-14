import re

from django import forms
from users.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class SignUpForm(forms.Form):
    email = forms.EmailField(label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"}))
    fullname = forms.CharField(label="이름", widget=forms.TextInput(attrs={"placeholder": "이름"}))
    
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={"placeholder": "비밀번호", "autocomplete": "new-password"}))
    password_confirm = forms.CharField(label="비밀번호 확인", widget=forms.PasswordInput(attrs={"placeholder": "비밀번호 확인", "autocomplete": "new-password"}))

    def clean(self):
        
        cleaned_data = super(SignUpForm, self).clean()
        
        email = cleaned_data.get("email")

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        match = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        validation = re.compile(match)
        
        if User.objects.filter(email=email).last():
            raise ValidationError({"email": "이미 존재하는 아이디입니다."})
        elif validation.match(str(password)) is None:
            raise ValidationError({"password": "비밀번호는 하나 이상의 문자, 숫자, 특수문자를 포함하여 8자리 이상으로 작성해주세요."})
        elif validation.match(str(password_confirm)) is None:
            raise ValidationError({"password_confirm": "비밀번호는 하나 이상의 문자, 숫자, 특수문자를 포함하여 8자리 이상으로 작성해주세요."})
        elif password and password_confirm:
            if password != password_confirm:
                raise ValidationError({"password": "비밀번호가 일치하지 않습니다."})

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일", widget=forms.EmailInput(attrs={"placeholder": "이메일"}))
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput(attrs={"placeholder": "비밀번호", "autocomplete": "new-password"}))

    
    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        user = User.objects.filter(email=email).last()

        if not user:
            raise ValidationError({"email": "올바른 이메일 주소를 입력해주세요."})

        elif not user.is_active:
            raise ValidationError({"email": "탈퇴한 회원입니다."})

        elif not check_password(password, user.password):
            raise ValidationError({"password": "잘못된 비밀번호입니다. 다시 확인하세요."})

        return cleaned_data

class MyInfoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class':'email-area', 'value' : self.instance.email, 'readonly': True, 'title': '이메일은 수정할 수 없습니다.'})
        self.fields['email'].required=False
        self.fields['phone'].required=True
        self.fields['password'].required=False
        self.fields['picture'].widget.attrs.update({'accept': 'image/gif, image/jpeg, image/png', })
    
    def clean(self):
        
        cleaned_data = super(MyInfoForm, self).clean()

        email = cleaned_data.get("email")
        old_password = User.objects.get(email=email).password

        phone = cleaned_data.get("phone")

        password = cleaned_data.get("password")

        match_ph = "^01([0|1|6|7|8|9])-?([0-9]{3,4})-?([0-9]{4})$"
        validation_ph = re.compile(match_ph)
        
        match_pw = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        validation_pw = re.compile(match_pw)
        
        if validation_ph.match(str(phone)) is None:
            raise ValidationError({"phone":"정확한 전화번호를 입력해주세요."})
        elif password:
            if validation_pw.match(str(password)) is None:
                raise ValidationError({"password": "비밀번호는 하나 이상의 문자, 숫자, 특수문자를 포함하여 8자리 이상으로 작성해주세요."})
            elif check_password(password, old_password):
                raise ValidationError({"password": "기존의 비밀번호와 동일합니다."})

        return cleaned_data
    
    class Meta:
        model=User
        fields=['email', 'fullname', 'phone', 'picture', 'password']
        widgets = {
            'fullname': forms.TextInput(attrs={'placeholder': '이름'}),
            'phone': forms.TextInput(attrs={'placeholder': '휴대폰'}),
            'picture' : forms.FileInput(attrs={'accept': 'image/gif, image/jpeg, image/png'}),
            'password' : forms.PasswordInput(attrs={'placeholder': '새로운 비밀번호를 입력해주세요.'})
        }