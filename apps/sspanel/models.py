import base64
import datetime

import markdown
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.utils import get_long_random_string, traffic_format
from apps.constants import THEME_CHOICES


class User(AbstractUser):
    '''SS账户模型'''

    @classmethod
    def proUser(cls):
        '''付费用户数量'''
        return len(cls.objects.filter(level__gt=0))

    @classmethod
    def userNum(cls):
        '''返回用户总数'''
        return len(cls.objects.all())

    @classmethod
    def todayRegister(cls):
        '''返回今日注册的用户'''
        today = datetime.datetime.combine(datetime.date.today(),
                                          datetime.time.min)
        return cls.objects.filter(date_joined__gt=today)

    @classmethod
    def clean_zombie_user(cls):
        '''
        删除僵尸用户
        '''
        users = cls.objects.all()
        for user in users:
            try:
                if user.ss_user.last_use_time == 0 and user.balance == 0:
                    user.delete()
            except ObjectDoesNotExist:
                user.delete()

    invitecode = models.CharField(verbose_name='邀请码', max_length=40)
    invited_by = models.PositiveIntegerField(verbose_name='邀请人id', default=1)
    balance = models.DecimalField(verbose_name='余额', decimal_places=2,
                                  max_digits=10, default=0, editable=True,
                                  null=True, blank=True,)
    invitecode_num = models.PositiveIntegerField(
        verbose_name='可生成的邀请码数量', default=settings.INVITE_NUM)
    level = models.PositiveIntegerField(verbose_name='用户等级', default=0,
                                        validators=[MaxValueValidator(9),
                                                    MinValueValidator(0), ])
    level_expire_time = models.DateTimeField(verbose_name='等级有效期',
                                             default=timezone.now)
    theme = models.CharField(verbose_name='主题', choices=THEME_CHOICES,
                             default=settings.DEFAULT_THEME, max_length=10)

    def __str__(self):
        return self.username

    def get_expire_time(self):
        '''返回等级到期时间'''
        return self.level_expire_time

    def get_sub_link(self):
        '''生成该用户的订阅地址'''
        token = base64.b64encode(bytes(self.username, 'utf-8')).decode('ascii')
        sub_link = settings.HOST + 'server/subscribe/' + token + '/'
        return sub_link

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'


class InviteCode(models.Model):
    '''邀请码'''

    INVITE_CODE_TYPE = ((1, '公开'), (0, '不公开'))

    code_type = models.IntegerField(
        verbose_name='类型', choices=INVITE_CODE_TYPE, default=0,)
    code_id = models.PositiveIntegerField(verbose_name='邀请人ID', default=1)
    code = models.CharField(verbose_name='邀请码', primary_key=True, blank=True,
                            max_length=40, default=get_long_random_string)
    time_created = models.DateTimeField(
        verbose_name='创建时间', editable=False, auto_now_add=True)
    isused = models.BooleanField(verbose_name='是否使用', default=False,)

    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name_plural = '邀请码'
        ordering = (
            'isused',
            '-time_created',
        )


class RebateRecord(models.Model):
    '''返利记录'''

    user_id = models.PositiveIntegerField(verbose_name='返利人ID', default=1)
    rebatetime = models.DateTimeField(
        verbose_name='返利时间', editable=False, auto_now_add=True)
    money = models.DecimalField(
        verbose_name='金额', decimal_places=2, null=True, default=0, max_digits=10, blank=True)

    class Meta:
        ordering = ('-rebatetime', )


class Donate(models.Model):
    @classmethod
    def totalDonateMoney(cls):
        '''返回捐赠总金额'''
        return sum([d.money for d in cls.objects.all()])

    @classmethod
    def totalDonateNums(cls):
        '''返回捐赠总数量'''
        return len(cls.objects.all())

    @classmethod
    def richPeople(cls):
        '''返回捐赠金额最多的前10名'''
        rec = {}
        for d in cls.objects.all():
            if d.user not in rec.keys():
                rec[d.user] = d.money
            else:
                rec[d.user] += d.money
        return sorted(rec.items(), key=lambda rec: rec[1], reverse=True)[:10]

    '''捐赠记录'''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='捐赠人')
    time = models.DateTimeField('捐赠时间', editable=False, auto_now_add=True)
    money = models.DecimalField(
        verbose_name='捐赠金额', decimal_places=2, max_digits=10, default=0, null=True, blank=True)

    def __str__(self):
        return '{}-{}'.format(self.user, self.money)

    class Meta:
        verbose_name_plural = '捐赠记录'
        ordering = ('-time', )


class MoneyCode(models.Model):
    '''充值码'''
    user = models.CharField(
        verbose_name='用户名', max_length=128, blank=True, null=True)
    time = models.DateTimeField('捐赠时间', editable=False, auto_now_add=True)
    code = models.CharField(verbose_name='充值码', unique=True,
                            blank=True, max_length=40, default=get_long_random_string)
    number = models.DecimalField(
        verbose_name='捐赠金额', decimal_places=2, max_digits=10, default=10, null=True, blank=True)
    isused = models.BooleanField(verbose_name='是否使用', default=False)

    def clean(self):
        # 保证充值码不会重复
        code_length = len(self.code or '')
        if 0 < code_length < 12:
            self.code = '{}{}'.format(self.code, get_long_random_string())
        else:
            self.code = get_long_random_string()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = '充值码'
        ordering = ('isused', )


class Goods(models.Model):
    '''商品'''

    STATUS_TYPE = (
        (1, '上架'),
        (-1, '下架'),
    )

    name = models.CharField(verbose_name='商品名字', max_length=128, default='待编辑')
    content = models.CharField(
        verbose_name='商品描述', max_length=256, default='待编辑')
    transfer = models.BigIntegerField(
        verbose_name='增加的流量', default=settings.GB)
    money = models.DecimalField(
        verbose_name='金额', decimal_places=2, max_digits=10, default=0, null=True, blank=True)
    level = models.PositiveIntegerField(verbose_name='设置等级', default=0, validators=[
                                        MaxValueValidator(9), MinValueValidator(0), ])
    days = models.PositiveIntegerField(verbose_name='设置等级时间(天)', default=1, validators=[
        MaxValueValidator(365), MinValueValidator(1)])
    status = models.SmallIntegerField('商品状态', default=1, choices=STATUS_TYPE)
    order = models.PositiveSmallIntegerField('排序', default=1)

    def __str__(self):
        return self.name

    def get_transfer(self):
        '''增加的流量'''
        return traffic_format(self.transfer)

    def get_days(self):
        '''返回增加的天数'''
        return '{}'.format(self.days)

    class Meta:
        verbose_name_plural = '商品'
        ordering = [
            'order',
        ]


class PurchaseHistory(models.Model):
    '''购买记录'''

    good = models.ForeignKey(
        Goods, on_delete=models.CASCADE, verbose_name='商品名')
    user = models.CharField(verbose_name='购买者', max_length=128)
    money = models.DecimalField(
        verbose_name='金额', decimal_places=2, max_digits=10, default=0, null=True, blank=True)
    purchtime = models.DateTimeField('购买时间', editable=False, auto_now_add=True)

    def __str__(self):
        return self.user

    class Meta:
        verbose_name_plural = '购买记录'
        ordering = ('-purchtime', )


class PayRecord(models.Model):
    '''充值流水单号记录'''

    username = models.CharField(
        verbose_name='用户名', max_length=64, blank=False, null=False)
    info_code = models.CharField(
        verbose_name='流水号', max_length=64, unique=True)
    time = models.DateTimeField(verbose_name='时间', auto_now_add=True)
    amount = models.DecimalField(
        verbose_name='金额', decimal_places=2, max_digits=10, default=0, null=True, blank=True)
    money_code = models.CharField(
        verbose_name='充值码', max_length=64, unique=True)
    charge_type = models.CharField(
        verbose_name='充值类型', max_length=10, default=1, help_text='1：支付宝 2：QQ钱包 3：微信支付')

    def __str__(self):
        return self.info_code

    class Meta:
        verbose_name_plural = '支付转账记录'
        ordering = ('-time', )


class PayRequest(models.Model):
    '''支付申请记录'''

    username = models.CharField(
        verbose_name='用户名', max_length=64, blank=False, null=False)
    info_code = models.CharField(
        verbose_name='流水号', max_length=64, unique=True)
    time = models.DateTimeField('时间', auto_now_add=True)
    amount = models.DecimalField(
        verbose_name='金额', decimal_places=2, max_digits=10, default=0, null=True, blank=True)
    charge_type = models.CharField(
        verbose_name='充值类型', max_length=10, default=1, help_text='1：支付宝 2：QQ钱包 3：微信支付')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '支付申请记录'
        ordering = ('-time', )


class Announcement(models.Model):
    '''公告界面'''
    time = models.DateTimeField('时间', auto_now_add=True)
    body = models.TextField('主体')

    def __str__(self):
        return '日期:{}'.format(str(self.time)[:9])

    # 重写save函数，将文本渲染成markdown格式存入数据库
    def save(self, *args, **kwargs):
        # 首先实例化一个MarkDown类，来渲染一下body的文本 成为html文本
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
        ])
        self.body = md.convert(self.body)
        # 调动父类save 将数据保存到数据库中
        super(Announcement, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = '系统公告'
        ordering = ('-time', )


class Ticket(models.Model):
    '''工单'''
    TICKET_CHOICE = ((1, '开启'), (-1, '关闭'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    time = models.DateTimeField(
        verbose_name='时间', editable=False, auto_now_add=True)
    title = models.CharField(verbose_name='标题', max_length=128)
    body = models.TextField(verbose_name='内容主体')
    status = models.SmallIntegerField(
        verbose_name='状态', choices=TICKET_CHOICE, default=1,)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '工单'
        ordering = ('-time', )
