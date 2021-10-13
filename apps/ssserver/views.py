import json
import base64

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import HttpResponse, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from apps.sspanel.models import User
from apps.sspanel.forms import UserForm
from .forms import ChangeSsPassForm, SSUserForm
from .models import METHOD_CHOICES, PROTOCOL_CHOICES, OBFS_CHOICES
from .models import (SSUser, TrafficLog, Node,
                     NodeInfoLog, NodeOnlineLog, AliveIp)


@permission_required('ssesrver')
def User_edit(request, pk):
    '''编辑ss_user的信息'''
    ss_user = SSUser.objects.get(pk=pk)
    # 当为post请求时，修改数据
    if request.method == "POST":
        # 对总流量部分进行修改，转换单GB
        data = request.POST.copy()
        data['transfer_enable'] = int(eval(
            data['transfer_enable']) * settings.GB)
        ssform = SSUserForm(data, instance=ss_user)
        userform = UserForm(data, instance=ss_user.user)
        if ssform.is_valid() and userform.is_valid():
            ssform.save()
            userform.save()
            # 修改账户密码
            passwd = request.POST.get('resetpass')
            if len(passwd) > 0:
                ss_user.user.set_password(passwd)
                ss_user.user.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:user_list"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {
                'ssform': ssform,
                'userform': userform,
                'ss_user': ss_user,
            }
            return render(request, 'backend/useredit.html', context=context)
    # 当请求不是post时，渲染form
    else:
        # 特别初始化总流量字段
        data = {'transfer_enable': ss_user.transfer_enable // settings.GB}
        ssform = SSUserForm(initial=data, instance=ss_user)
        userform = UserForm(instance=ss_user.user)
        context = {
            'ssform': ssform,
            'userform': userform,
            'ss_user': ss_user,
        }
        return render(request, 'backend/useredit.html', context=context)


@login_required
def ChangeSsPass(request):
    '''改变用户ss连接密码'''
    ss_user = request.user.ss_user

    if request.method == 'POST':
        form = ChangeSsPassForm(request.POST)

        if form.is_valid():
            # 获取用户提交的password
            ss_pass = request.POST.get('password')
            ss_user.password = ss_pass
            ss_user.save()
            messages.success(request, "请及时更换客户端密码！", extra_tags="修改成功！")
            return HttpResponseRedirect(reverse('sspanel:userinfo_edit'))
        else:
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ChangeSsPassForm()
        return render(request, 'sspanel/sspasschanged.html', {'form': form})


@login_required
def ChangeSsMethod(request):
    '''改变用户ss加密'''
    ss_user = request.user.ss_user

    if request.method == 'POST':
        ss_method = request.POST.get('method')
        ss_user.method = ss_method
        ss_user.save()
        messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
        return HttpResponseRedirect(reverse('sspanel:userinfo_edit'))


@login_required
def ChangeSsProtocol(request):
    '''改变用户ss协议'''
    ss_user = request.user.ss_user

    if request.method == 'POST':
        ss_protocol = request.POST.get('protocol')
        ss_user.protocol = ss_protocol
        ss_user.save()
        messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
        return HttpResponseRedirect(reverse('sspanel:userinfo_edit'))


@login_required
def ChangeSsObfs(request):
    '''改变用户ss连接混淆'''
    ss_user = request.user.ss_user

    if request.method == 'POST':
        ss_obfs = request.POST.get('obfs')
        ss_user.obfs = ss_obfs
        ss_user.save()
        messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
        return HttpResponseRedirect(reverse('sspanel:userinfo_edit'))


def subscribe(request, token):
    '''
    返回ssr订阅链接
    '''
    user = base64.b64decode(token).decode('utf8')
    # 验证token
    try:
        user = User.objects.get(username=user)
        ss_user = user.ss_user
        # 遍历该用户所有的节点
        node_list = Node.objects.filter(level__lte=user.level, show=1)
        # 生成订阅链接部分
        sub_code = 'MAX={}\n'.format(len(node_list))
        for node in node_list:
            sub_code = sub_code + node.get_ssr_link(ss_user) + "\n"
        sub_code = base64.b64encode(bytes(sub_code, 'utf8')).decode('ascii')
        return HttpResponse(sub_code)
    except:
        return HttpResponse('ERROR')


@login_required
def node_config(request):
    '''返回节点json配置'''
    user = request.user
    node_list = Node.objects.filter(level__lte=user.level, show=1)
    data = {'configs': []}
    for node in node_list:
        if node.custom_method == 0:
            data['configs'].append({
                "remarks": node.name,
                "enable": True,
                "password": user.ss_user.password,
                "method": node.method,
                "server": node.server,
                "obfs": node.obfs,
                "protocol": node.protocol,
                "server_port": user.ss_user.port,
                "remarks_base64": base64.b64encode(
                    bytes(node.name, 'utf8')).decode('ascii'),
            })
        else:
            data['configs'].append({
                "remarks": node.name,
                "enable": True,
                "password": user.ss_user.password,
                "method": user.ss_user.method,
                "server": node.server,
                "obfs": user.ss_user.obfs,
                "protocol": user.ss_user.protocol,
                "server_port": user.ss_user.port,
                "remarks_base64": base64.b64encode(
                    bytes(node.name, 'utf8')).decode('ascii')
            })
    response = StreamingHttpResponse(json.dumps(data, ensure_ascii=False))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename="ss.json"'
    return response
