# 引入S3BotoStorage类
from storages.backends.s3boto import S3BotoStorage

# 创建静态文件存储类，指定存储位置为'static'
StaticRootS3BotoStorage = lambda: S3BotoStorage(location='static')

# 创建媒体文件存储类，指定存储位置为'media'
MediaRootS3BotoStorage = lambda: S3BotoStorage(location='media')