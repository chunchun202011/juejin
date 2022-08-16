from binascii import b2a_hex
from random import randint
import re
import serial

from Crypto.SelfTest.st_common import a2b_hex
from MySQLdb import DatabaseError
import logging

from Crypto.Cipher import AES
from aes import aes
from django.utils.baseconv import base64

import user
from libs.yuntongxun.sms import CCP
from django_redis import get_redis_connection
from pymysql import DatabaseError

from user import models
from user.models import User
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse, response
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from util.response_code import RETCODE
logger = logging.getLogger('django')


# Create your views here.
# 注册视图
class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    def post(self,request):
        """
        1.接收数据
        2.验证数据
            2.1 参数是否齐全
            2.2 手机号的格式是否正确
            2.3 密码是否符合格式
            2.4 密码和确认密码要一致
            2.5 短信验证码是否和redis中的一致
        3.保存注册信息
        4.返回响应跳转到指定页面
        :param request:
        :return:
        """
        # 1.接收数据
        userPhone = request.POST.get('userPhone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        verCode = request.POST.get('verCode')
        # 2.验证数据
        #     2.1 参数是否齐全
        if not all([userPhone, password, password2, verCode]):
            return HttpResponseBadRequest('缺少必要的参数')
        #     2.2 手机号的格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', userPhone):
            return HttpResponseBadRequest('手机号不符合规则')
        #     2.3 密码是否符合格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码，密码是数字，字母')
        #     2.4 密码和确认密码要一致
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        #     2.5 短信验证码是否和redis中的一致
        redis_conn = get_redis_connection('default')
        redis_sms_code=redis_conn.get('sms:%s' % userPhone)
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if verCode != redis_sms_code.decode():
            return HttpResponseBadRequest('短信验证码不一致')
        # 3.保存注册信息
        # create_user 对密码进行加密
        key = "1234567812345678"
        iv = "1234567812345678"
        userPassword = AESUtil.encryt(password, key, iv)  # 加密
        # d = AESUtil.decrypt(userPassword, key, iv)  # 解密
        # print("加密:", userPassword)
        # print("解密:", d)
        pc = AESUtil('keyskeyskeyskeys')  # 初始化密钥
        userPassword = pc.encrypt(password)  # 加密

        try:
            user= User.objects.create_user(username=userPhone,
                                      userPhone=userPhone,
                                      userPassword=userPassword)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

# 短信验证码视图
class VerCodeView(View):
    def get(self, request):
        '''
        1.接收参数
        2.参数的验证
            2.1 验证参数是否齐全（手机号userPhone,图形验证码image_code,唯一编号uuid）
        3.生成短信验证码
        4.保存短信验证码到redis中
        5.发送短信
        6.返回响应
        :param request:
        :return:
        '''

    # 1. 接收参数
        userPhone = request.GET.get('userPhone')
        # image_code = request.GET.get('image_code')
        # uuid = request.GET.get('uuid')

    # 2.参数的验证
        if not all({userPhone}):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR,'errmsg':'缺少必要的参数'})

    #    2.2图片验证码的验证
    #       连接redis, 获取redis中的图片验证码
        redis_conn = get_redis_connection('default')

    # 3.生成短信验证码(4位)
        verCode = '%04d' % randint(1000, 9999)
    # 为了后期使用方便，将短信验证码保存到日志中
        logger.info(verCode)
    # 4.保存短信验证码到redis中
        redis_conn.setex('sms:%s' % userPhone, 300, verCode)
    # 5.发送短信
        # 参数1：测试手机号
        # 参数2：模板内容列表 (1) 短信验证码 (2) 分钟有效
        # 参数3：模板 免费开发测试用的模板ID为1
        CCP().send_template_sms(userPhone,[verCode,5],1)
    # 6.返回响应
        return JsonResponse({'code':RETCODE.OK,'errmsg':'短信发送成功'})



# 加密解密包（加解密方法在里面，可以通过调用encryt加密，decryt解密）
class AESUtil:

    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size

    @staticmethod
    def encryt(str:'str', key:'str', iv:'str')->'bytes':
        key = key.encode('utf-8')
        iv = iv.encode('utf-8')
        # str = str.encode('utf-8')

        cipher = AES.new(key, AES.MODE_CBC,iv)
        x = AESUtil.__BLOCK_SIZE_16 - (len(str) % AESUtil.__BLOCK_SIZE_16)
        if x != 0:
            str = str + chr(x)*x
            str = bytes(str, encoding='utf-8')
        msg = cipher.encrypt(str)
        msg = base64.urlsafe_b64encode(msg).replace('=', '')
        msg = base64.b64encode(msg)
        return msg

    @staticmethod
    def decrypt(enStr, key, iv):
        cipher = AES.new(key, AES.MODE_CBC, iv)
        enStr += (len(enStr) % 4) * "="
        # decryptByts = base64.urlsafe_b64decode(enStr)
        decryptByts = base64.b64decode(enStr)
        msg = cipher.decrypt(decryptByts)
        paddingLen = ord(msg[len(msg)-1])
        return msg[0:-paddingLen]

# class AESUtil(object):
#     from serial import Serial
#     def __init__(self, key):
#         self.key = key.encode('utf-8')
#         self.mode = AES.MODE_CBC
#     import serial

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    # def encrypt(self, text):
    #     if text: self.serial.write(text.encode())
    #     cryptor = AES.new(self.key, self.mode, b'0000000000000000')
    #     # 这里密钥key 长度必须为16（AES-128）,
    #     # 24（AES-192）,或者32 （AES-256）Bytes 长度
    #     # 目前AES-128 足够目前使用
    #     length = 16
    #     count = len(text)
    #     if count < length:
    #         add = (length - count)
    #         # \0 backspace
    #         # text = text + ('\0' * add)
    #         text = text + ('\0' * add).encode('utf-8')
    #     elif count > length:
    #         add = (length - (count % length))
    #         # text = text + ('\0' * add)
    #         text = text + ('\0' * add).encode('utf-8')
    #     self.ciphertext = cryptor.encrypt(text)
    #     # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
    #     # 所以这里统一把加密后的字符串转化为16进制字符串
    #     return b2a_hex(self.ciphertext)
    #
    # # 解密后，去掉补足的空格用strip() 去掉
    # def decrypt(self, text):
    #     cryptor = AES.new(self.key, self.mode, b'0000000000000000')
    #     plain_text = cryptor.decrypt(a2b_hex(text))
    #     # return plain_text.rstrip('\0')
    #     return bytes.decode(plain_text).rstrip('\0')

# class AESUtil(str):
#     iv = '1234567887654321'
#     key = 'miyaoxuyao16ziji'
#     # 将原始的明文用空格填充到16字节
#     def pad(data):
#         pad_data = data
#         for i in range(0, 16 - len(data)):
#             pad_data = pad_data + ' '
#         return pad_data
#
#
#     # 将明文用AES加密
#     def AES_en(key, data):
#         # 将长度不足16字节的字符串补齐
#         if len(data) < 16:
#             data = pad(data)
#         # 创建加密对象
#         AES_obj = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
#         # 完成加密
#         AES_en_str = AES_obj.encrypt(data.encode("utf-8"))
#         # 用base64编码一下
#         AES_en_str = base64.b64encode(AES_en_str)
#         # 最后将密文转化成字符串
#         AES_en_str = AES_en_str.decode("utf-8")
#         return AES_en_str
#
#
#     def AES_de(key, data):
#         # 解密过程逆着加密过程写
#         # 将密文字符串重新编码成二进制形式
#         data = data.encode("utf-8")
#         # 将base64的编码解开
#         data = base64.b64decode(data)
#         # 创建解密对象
#         AES_de_obj = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
#         # 完成解密
#         AES_de_str = AES_de_obj.decrypt(data)
#         # 去掉补上的空格
#         AES_de_str = AES_de_str.strip()
#         # 对明文解码
#         AES_de_str = AES_de_str.decode("utf-8")
#         return AES_de_str

# class AESUtil(str):
#     key = b'12345678abcdefgh'
#     iv = b'qwertyui12345678'
#     aes = AES.new(key, AES.MODE_CBC, iv=iv)
#
#     str1 = bytes(str)
#     def encrypt(str1):
#         # 加密
#         en_data = aes.encrypt(str1)
#         # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
#         # 所以这里统一把加密后的字符串转化为16进制字符串
#         return b2a_hex(en_data)
#
#     def decrypt(str):
#         str2 = bytes(str)
#         key = b'12345678abcdefgh'
#         iv = b'qwertyui12345678'
#         aes2 = AES.new(key,AES.MODE_CBC, iv=iv)  # 构建AES加密对象
#         de_data = aes2.decrypt(str2)
#         return


# 登录视图
class LoginView(View):

    def get(self, request):

        return render(request, 'login.html')
    def post(self,request):
        '''
        1.接收参数
        2.参数的验证
            2.1 验证手机号是否符合规则
            2.2 验证密码
        3.用户认证登录
        4.状态的保持
        5.根据用户的选择是否记住登录状态
        6.为了首页显示需要设置cookie
        7.返回响应
        :param request:
        :return:
        '''
    #  1.接收参数
        userPhone = request.POST.get('userPhone')
        userPassword1 = request.POST.get('userPassword')
        userPassword2 = str(userPassword1)
        key = "1234567812345678"
        iv = "1234567812345678"
        # userPassword = AESUtil.encryt(userPassword1, key, iv)  # 加密
        # pc = AESUtil('keyskeyskeyskeys')  # 初始化密钥
        # userPassword = pc.encrypt(userPassword2)  # 加密
        userPassword = AESUtil.encryt(userPassword2, key, iv)
        remember = request.POST.get('remember')  # 是否自动登录
    #   2.参数的验证
        if userPhone and userPassword:
            counter = user.objects.filter(userPhone=userPhone, userPassword=userPassword).count()
            if counter == 1:
                # return HttpResponse('登录成功！')
                return HttpResponseRedirect('/user/index/')
            if counter != 1:
                return HttpResponse('请输入正确账号或密码！')

        # 检测是否被记住，cookies是否存在
        if remember == 'on':
            # 获取cookies
            userPhone = request.COOKIES.get("userPhone")
            userPassword = request.COOKIES.get("userPassword")
            # 获取登录用户信息
            login_user = models.User.objects.get(userPhone=userPhone, userPassword=userPassword)
            # 返回登录成功后页面
            return render(request, "index.html", {"login_user": login_user})
        else:
            # 进入未登录状态的主页
             return render(request, "login.html")





