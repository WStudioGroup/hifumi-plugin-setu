from nonebot.plugin import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GROUP_ADMIN,
    GROUP_OWNER,
    PRIVATE_FRIEND,
)
from .handle import upload_setu, send_result, setu, size, r18

on_command(
    "图库色图，上传", 
    block = True, 
    permission = GROUP | PRIVATE_FRIEND, 
    handlers = [
        upload_setu.upload_event_group,
        upload_setu.upload_event_private
    ]
)

on_command(
    "发送色图审核通知", 
    priority = 50, 
    block = True, 
    permission = SUPERUSER,
    handlers = [
        send_result.send_result_event
    ]
)

on_command(
    "图库大小",
    priority = 50,
    block = True,
    handlers = [
        size.size_event
    ]
)

on_command(
    "获取图库色图", 
    block = True, 
    permission = GROUP | PRIVATE_FRIEND,
    handlers = [
        setu.setu_event_group,
        setu.setu_event_private
    ]
)

on_command(
    "图库色图，开启r18", 
    block = True, 
    permission = GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    handlers = [
        r18.enable
    ]
)

on_command(
    "图库色图，关闭r18", 
    block = True, 
    permission = GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    handlers = [
        r18.disable
    ]
)

on_command(
    "清空审核记录", 
    block = True, 
    permission = SUPERUSER,
    handlers = [
        send_result.clear
    ]
)

