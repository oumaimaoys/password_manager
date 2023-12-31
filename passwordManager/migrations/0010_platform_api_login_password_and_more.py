# Generated by Django 4.2.3 on 2023-08-21 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passwordManager', '0009_alter_platform_instance_url_alter_platform_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='api_login_password',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='platform',
            name='api_login_username',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(default=None, max_length=255),
        ),
    ]
