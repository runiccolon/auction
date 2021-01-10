import random
import uuid

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from api.serializer.account import LoginSerializer, MessageSerializer


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        """
        1.校验手机号是否合法
        2.校验验证码,redis
            - 无验证码
            - 有验证码,输入错误
            - 有验证码,成功
        3.数据库中获取用户信息(已注册用户获取/新用户创建)
        4.将一些信息返回给小程序
        """
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response({"status": False, "message": "验证码错误"})
        # 去数据库中获取用户信息(获取/创建)
        phone = ser.validated_data.get('phone')
        user_object, flag = models.UserInfo.objects.get_or_create(phone=phone)
        user_object.token = str(uuid.uuid4())
        user_object.save()

        return Response({'status': True, "data": {"token": user_object.token, "phone": phone}})

        # user = models.UserInfo.objects.filter(phone=phone).first()
        # if not user:
        #     models.UserInfo.objects.create(phone=phone,token=str(uuid.uuid4()))
        # else:
        #     user.token = str(uuid.uuid4())
        #     user.save()


class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机短信验证码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # 1.获取手机号
        # 2.手机号格式校验
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status': False, 'message': '手机格式错误'})
        phone = ser.validated_data.get('phone')
        # 3.生成随机验证码
        random_code = random.randint(1000, 9999)

        # 4.验证码发送到手机上, 购买服务器进行发送短信
        # result = send_msg(phone, random_code)
        # if not result:
        #     return Response({'status': False, 'message': '短信发送失败'})

        print(random_code)
        # 5.保留手机号和验证码(30s)过期
        """
            5.1 搭建redis服务(云redis)
            5.2 django中方便使用redis的模块 django-redis
                配置: settings
        """
        conn = get_redis_connection()
        conn.set(phone, random_code, ex=60)
        return Response({"status": True, "message": "发送成功"})
