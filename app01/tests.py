from django.test import TestCase

# Create your tests here.

import redis

# 直接连接redis
# conn = redis.Redis(host="192.168.3.40", port=6379, password=123456, encoding="utf-8")
# # 设置键值:15131255089="9999" 且超时间为10秒(值写入到redis时会自动转字符串)
# conn.set('15131255089', 9999, ex=10)
#
# # 根据键获取值：如果存在获取值(获取到的是字节类型);不存在则返回None
# value = conn.get("15131255089")
# print(value)

# 连接池连接redis
# 创建redis连接池（默认连接池最大连接数2**31=2147483648
pool = redis.ConnectionPool(host="192.168.3.40", port=6379, password="123456", encoding="utf-8", max_connections=1000)
# 去连接池中获取一个连接数
conn = redis.Redis(connection_pool=pool)
# 设置键值：13589787879="999" 且超时时间为10秒(值写入到redis时会自动转换字符串）
conn.set("name", "青城子", ex=10)
# 根据键获取值：如果存在获取值（获取到的是字节类型）；不存在则返回None
value = conn.get("mobile_phone")
print(value)
