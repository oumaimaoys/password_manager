# Generated by Django 4.2.3 on 2023-08-22 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passwordManager', '0011_alter_platform_api_login_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='user_id_on_platform',
            field=models.CharField(default=None, max_length=250),
        ),
    ]
