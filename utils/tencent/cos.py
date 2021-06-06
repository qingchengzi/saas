#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 青城子
# datetime： 2021/5/16 16:31
# ide： PyCharm

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings
from qcloud_cos.cos_exception import CosServiceError


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
    # 开启跨域
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
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


def check_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    client = CosS3Client(config)
    print("到自豪的啊", key)
    data = client.head_object(
        Bucket=bucket,
        Key=key,
    )
    return data


def credential(bucket, region):
    """ 获取cos上传临时凭证 """
    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 1800,
        # 固定密钥 id
        'secret_id': settings.TENCENT_COS_ID,
        # 固定密钥 key
        'secret_key': settings.TENCENT_COS_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }
    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def delete_bucket(bucket, region):
    """
    删除桶
    # 先删除桶中所有文件
    删除桶中所有碎片
    删除桶
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY, )
    client = CosS3Client(config)
    try:
        # 找到桶中的所有文件,腾讯COS一次最多返回1000个文件,所有需要循环删除
        while True:
            part_objects = client.list_objects(bucket)
            # 已经删除完毕，获取不到值
            contents = part_objects.get("Contents")
            if not contents:
                break
            # 批量删除
            objects = {
                "Quiet": "true",
                "Object": [{"Key": item["Key"]} for item in contents]
            }
            client.delete_objects(bucket, objects)
            # 最后一个文件时=false
            if part_objects["IsTruncated"] == "false":
                break

        # 找到碎片 & 删除
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            # Upload为空说明没有碎片
            uploads = part_uploads.get("Upload")
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket, item.get("Key"), item.get["UploadId"])

            # 最后一个文件时=false
            if part_uploads["IsTruncated"] == "false":
                break

        client.delete_bucket(bucket)
    except CosServiceError as err:
        pass
