import json
import base64

from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import StreamingHttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required

from .models import Suser, Node
from apps.sspanel.models import User
from apps.sspanel.forms import UserForm
from .forms import ChangeSsPassForm, SuserForm


@permission_required("ssesrver")
def user_edit(request, user_id):
    """编辑ss_user的信息"""
    ss_user = Suser.objects.get(user_id=user_id)
    # 当为post请求时，修改数据
    if request.method == "POST":
        # 对总流量部分进行修改，转换单GB
        data = request.POST.copy()
        data["transfer_enable"] = int(eval(data["transfer_enable"]) * settings.GB)
        ssform = SuserForm(data, instance=ss_user)
        userform = UserForm(data, instance=ss_user.user)
        if ssform.is_valid() and userform.is_valid():
            ssform.save()
            userform.save()
            # 修改账户密码
            passwd = request.POST.get("resetpass")
            if len(passwd) > 0:
                user = ss_user.user
                user.set_password(passwd)
                user.save()
            messages.success(request, "数据更新成功", extra_tags="修改成功")
            return HttpResponseRedirect(reverse("sspanel:user_list"))
        else:
            messages.error(request, "数据填写错误", extra_tags="错误")
            context = {"ssform": ssform, "userform": userform, "ss_user": ss_user}
            return render(request, "backend/useredit.html", context=context)
    # 当请求不是post时，渲染form
    else:
        # 特别初始化总流量字段
        data = {"transfer_enable": ss_user.transfer_enable // settings.GB}
        ssform = SuserForm(initial=data, instance=ss_user)
        userform = UserForm(instance=ss_user.user)
        context = {"ssform": ssform, "userform": userform, "ss_user": ss_user}
        return render(request, "backend/useredit.html", context=context)


@login_required
@require_http_methods(["POST"])
def change_ss_pass(request):
    """改变用户ss连接密码"""
    ss_user = request.user.ss_user

    if request.method == "POST":
        form = ChangeSsPassForm(request.POST)

        if form.is_valid():
            # 获取用户提交的password
            ss_pass = request.POST.get("password")
            ss_user.password = ss_pass
            ss_user.save()
            messages.success(request, "请及时更换客户端密码！", extra_tags="修改成功！")
            return HttpResponseRedirect(reverse("sspanel:userinfo_edit"))
        else:
            messages.error(request, "新的客户端密码格式不正确！", extra_tags="修改失败！")
            return HttpResponseRedirect(reverse("sspanel:userinfo_edit"))
    else:
        form = ChangeSsPassForm()
        return render(request, "sspanel/sspasschanged.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def change_ss_method(request):
    """改变用户ss加密"""
    ss_user = request.user.ss_user
    ss_method = request.POST.get("method")
    ss_user.method = ss_method
    ss_user.save()
    messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
    return HttpResponseRedirect(reverse("sspanel:userinfo_edit"))


@login_required
@require_http_methods(["POST"])
def change_ss_protocol(request):
    """改变用户ss协议"""
    ss_user = request.user.ss_user
    ss_protocol = request.POST.get("protocol")
    ss_user.protocol = ss_protocol
    ss_user.save()
    messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
    return HttpResponseRedirect(reverse("sspanel:userinfo_edit"))


@login_required
@require_http_methods(["POST"])
def change_ss_obfs(request):
    """改变用户ss连接混淆"""
    ss_user = request.user.ss_user
    ss_obfs = request.POST.get("obfs")
    ss_user.obfs = ss_obfs
    ss_user.save()
    messages.success(request, "请及时更换客户端配置！", extra_tags="修改成功！")
    return HttpResponseRedirect(reverse("sspanel:userinfo_edit"))


def subscribe(request):
    """
    返回ssr订阅链接
    """
    token = request.GET.get("token", "")
    username = base64.b64decode(token).decode()
    # 验证token
    user = get_object_or_404(User, username=username)
    ss_user = user.ss_user
    # 遍历该用户所有的节点
    node_list = Node.objects.filter(level__lte=user.level, show=1)
    # 生成订阅链接部分
    sub_code = "MAX={}\n".format(len(node_list))
    for node in node_list:
        sub_code = sub_code + node.get_node_link(ss_user) + "\n"
    sub_code = base64.b64encode(bytes(sub_code, "utf8")).decode("ascii")
    resp_ok = StreamingHttpResponse(sub_code)
    resp_ok["Content-Type"] = "application/octet-stream; charset=utf-8"
    resp_ok["Content-Disposition"] = "attachment; filename={}.txt".format(token)
    resp_ok["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp_ok["Content-Length"] = len(sub_code)
    return resp_ok


@login_required
def node_config(request):
    """返回节点json配置"""
    user = request.user
    ss_user = user.ss_user
    node_list = Node.objects.filter(level__lte=user.level, show=1)
    data = {"configs": []}
    for node in node_list:
        if node.node_type == 1:
            #  单端口模式
            data["configs"].append(
                {
                    "remarks": node.name,
                    "server_port": node.port,
                    "remarks_base64": base64.b64encode(bytes(node.name, "utf8")).decode(
                        "ascii"
                    ),
                    "enable": True,
                    "password": node.password,
                    "method": node.method,
                    "server": node.server,
                    "obfs": node.obfs,
                    "obfs_param": node.obfs_param,
                    "protocol": node.protocol,
                    "protocol_param": "{}:{}".format(ss_user.port, ss_user.password),
                }
            )
        elif node.custom_method == 1:
            data["configs"].append(
                {
                    "remarks": node.name,
                    "server_port": ss_user.port,
                    "remarks_base64": base64.b64encode(bytes(node.name, "utf8")).decode(
                        "ascii"
                    ),
                    "enable": True,
                    "password": ss_user.password,
                    "method": ss_user.method,
                    "server": node.server,
                    "obfs": ss_user.obfs,
                    "protocol": ss_user.protocol,
                }
            )
        else:
            data["configs"].append(
                {
                    "remarks": node.name,
                    "server_port": ss_user.port,
                    "remarks_base64": base64.b64encode(bytes(node.name, "utf8")).decode(
                        "ascii"
                    ),
                    "enable": True,
                    "password": ss_user.password,
                    "method": node.method,
                    "server": node.server,
                    "obfs": node.obfs,
                    "protocol": node.protocol,
                }
            )
    response = StreamingHttpResponse(json.dumps(data, ensure_ascii=False))
    response["Content-Type"] = "application/octet-stream"
    response["Content-Disposition"] = 'attachment; filename="ss.json"'
    return response
