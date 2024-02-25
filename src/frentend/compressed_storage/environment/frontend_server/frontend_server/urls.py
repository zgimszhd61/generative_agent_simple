"""frontend_server URL 配置

`urlpatterns` 列表将 URL 路由到视图。更多信息请参阅:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
示例:
函数视图
    1. 添加导入语句:  from my_app import views
    2. 添加 URL 到 urlpatterns:  path('', views.home, name='home')
基于类的视图
    1. 添加导入语句:  from other_app.views import Home
    2. 添加 URL 到 urlpatterns:  path('', Home.as_view(), name='home')
包含另一个 URL 配置
    1. 导入 include() 函数: from django.urls import include, path
    2. 添加 URL 到 urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from translator import views as translator_views

urlpatterns = [
    # Landing 页面
    url(r'^$', translator_views.landing, name='landing'),
    # 模拟器主页
    url(r'^simulator_home$', translator_views.home, name='home'),
    # 演示
    url(r'^demo/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<play_speed>[\w-]+)/$', translator_views.demo, name='demo'),
    # 重新播放
    url(r'^replay/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/$', translator_views.replay, name='replay'),
    # 重新播放个人状态
    url(r'^replay_persona_state/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<persona_name>[\w-]+)/$', translator_views.replay_persona_state, name='replay_persona_state'),
    # 处理环境
    url(r'^process_environment/$', translator_views.process_environment, name='process_environment'),
    # 更新环境
    url(r'^update_environment/$', translator_views.update_environment, name='update_environment'),
    # 路径测试器
    url(r'^path_tester/$', translator_views.path_tester, name='path_tester'),
    # 更新路径测试器
    url(r'^path_tester_update/$', translator_views.path_tester_update, name='path_tester_update'),
    path('admin/', admin.site.urls),
]
