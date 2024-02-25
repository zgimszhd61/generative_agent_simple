"""
前端服务器项目的WSGI配置。

它将WSGI可调用项公开为名为“application”的模块级变量。

有关此文件的更多信息，请参见
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# 设置默认的Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_server.settings')

# 获取WSGI应用程序
application = get_wsgi_application()