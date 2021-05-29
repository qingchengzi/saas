#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/16 16:31 
# ide： PyCharm


from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings


def create_bucket(bucket, region="ap-guangzhou"):
    """
    创建桶
    :param bucket: 桶名称
    :param region: 区域
    :return:
    """
    secret_id = settings.TENCENT_COS_ID
    secret_key = settings.TENCENT_COS_KEY

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, )

    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL="public-read",  # private / public-read / public-read-write
    )


def upload_file(bucket, region, file_object, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    client = CosS3Client(config)
    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key  # 上传到桶之后的文件名
    )
    # 返回图片路径，预览时用
    return "https://{0}.cos.{1}.myqcloud.com/{2}".format(bucket, region, key)


def delete_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key  # 上传到桶之后的文件名
    )


def delete_file_list(bucket, region, key_list):
    """
    批量删除
    :param bucket:
    :param region:
    :param key:
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects
    )
