#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/16 15:32 
# ide： PyCharm

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = 'AKIDxiDSQ7XgYAVZNt86oFPItEI4ZomUv5ya'  # 替换为用户的 secretId
secret_key = 'MRGo5B4g15tQItDKAj13oIUR6UbR0IJ3'  # 替换为用户的 secretKey

region = 'ap-guangzhou'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, )

client = CosS3Client(config)

# 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
# response = client.upload_file(
#     Bucket='tianxiang-1253858492',  # 上传文件时桶的名称
#     LocalFilePath='code.png',  # 本地文件的路径
#     Key='p1.png',  # 上传到桶之后的文件名
# )
# print(response['ETag'])

# 创建桶
response = client.create_bucket(
    Bucket='tianxx-1253858492',
    ACL="public-read",  # private / public-read / public-read-write
)
