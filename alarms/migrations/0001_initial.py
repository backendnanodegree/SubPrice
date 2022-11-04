# Generated by Django 3.2.13 on 2022-11-04 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='갱신일')),
                ('d_day', models.PositiveSmallIntegerField(choices=[(1, '1일전'), (2, '2일전'), (3, '3일전'), (4, '4일전'), (5, '5일전'), (6, '6일전'), (7, '7일전')], help_text='선택 시, 해당 일자에 메일이 발송됩니다.', null=True, verbose_name='카테고리 종류')),
                ('is_active', models.BooleanField(default=False, verbose_name='메일 발송 여부')),
                ('subscription', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alarm_subscription', to='subscriptions.subscription', verbose_name='구독정보')),
            ],
            options={
                'verbose_name': '알림 정보',
                'verbose_name_plural': '알림 정보 목록',
            },
        ),
        migrations.CreateModel(
            name='AlarmHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='갱신일')),
                ('content', models.TextField(blank=True, default='', help_text='발송시 메일 내용을 그대로 넣어줍니다.', null=True, verbose_name='알림 내역')),
                ('is_success', models.BooleanField(default=False, verbose_name='발송 성공 여부')),
                ('traceback', models.TextField(blank=True, default='', verbose_name='발송 실패 원인')),
                ('alarm', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='alarms.alarm', verbose_name='알림')),
            ],
            options={
                'verbose_name': '알림 내역',
                'verbose_name_plural': '알림 내역 목록',
            },
        ),
    ]