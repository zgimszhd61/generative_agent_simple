#!/usr/bin/env python
"""Django的命令行实用工具，用于管理任务。"""
import os
import sys


def main():
    # 设置 Django 使用的配置文件
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend_server.settings')
    try:
        # 导入 Django 的执行命令行模块
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 若导入失败，给出相关提示
        raise ImportError(
            "无法导入 Django。您确定已安装并且在 PYTHONPATH 环境变量中可用吗？您是否忘记激活虚拟环境？"
        ) from exc
    # 执行 Django 命令行
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
