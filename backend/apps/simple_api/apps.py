from django.apps import AppConfig


class SimpleApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.simple_api'
    verbose_name = '简单API（免登录）'
