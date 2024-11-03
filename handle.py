from nonebot.matcher import Matcher
from nonebot.adapters import Event as a_event
from nonebot.drivers.httpx import httpx # type: ignore
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import require
require("nonebot_plugin_waiter")
from nonebot_plugin_waiter import waiter
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment,
    Message as onebot_message
)
import json
from .util import check_image, download_url
from .data import set_r18, get_r18

endpoint = "http://127.0.0.1:5264"

def hide_id(id: int) -> str:
    """
    隐藏id，支持群号和qq号

    参数:
        id(int): 要隐藏的id
    """
    result = str(id)[:3]
    for i in range(3, len(str(id))-3):
        result += "*"
    return result+str(id)[len(str(id))-3:]

class upload_setu:
    @staticmethod
    async def __upload_event__(upload: Matcher, bot: Bot, event: GroupMessageEvent|PrivateMessageEvent):
        imgs = []
        await upload.send("请老师发送要上传的图片：\n（多张请逐个发送）\n发送“结束”结束接收图片\n发送“取消”以取消")

        # 获取图片
        @waiter(waits=["message"], keep_session=True)
        async def check_image(event: a_event):
            message = event.get_message()
            if message.has("image"):
                return message.get("image")
            return event.get_plaintext()
        
        async for resp in check_image(
            timeout=240, 
            retry=15, 
            prompt="请老师发送要上传的图片\n（多张请逐个发送）\n发送“取消”以取消\n发送“结束”以结束接收图片\n剩余次数：{count}"):
            if resp is None:
                await upload.send("老师走神啦！等待超时，请重试！")
                break
            if type(resp) is str:
                if resp == "取消":
                    await upload.finish("已取消~")
                elif resp == "结束":
                    # 结束接收图片，跳出循环
                    break
            elif type(resp) is onebot_message:
                if resp == []:
                    await upload.finish("老师又在开小差！只能发送图片哦，请重试！")
                if len(resp) > 15:
                    await upload.finish("老师，最多只能同时上传15张图片哦！请重试！")
                for i in resp:
                    img = {
                        "name": i.data["file_unique"],  # 图片名称
                        "url": i.data["url"],           # 图片链接
                        "tags": [],                     # 标签
                        "uid": event.sender.user_id,    # 上传者QQ号
                        "gid": event.group_id if isinstance(event,GroupMessageEvent) else 0,
                        # 是群消息则为群号，否则为私聊上传，填入0
                        "bot_id": event.self_id         # 机器人QQ号，用于识别不同机器上传的图片，避免通知不到位
                    }
                    imgs.append(img)
                    continue
            else:
                await upload.send(str(type(resp)))
        else:
            await upload.send("输入失败！")

        if not imgs:
            await upload.finish("老师没有上传图片，已退出~")

        for i in imgs:
            msg: onebot_message = "请老师为这张图片打上标签,每个标签用空格隔开：\n标注人物名称,带有英文名称最好~\nr18图片请直接加上“r18”标签!\n例如: 日奈 空崎日奈 Hina 亚子 天雨亚子 Ako\n"+MessageSegment.image(i["url"])
            await upload.send(msg)

            @waiter(waits=["message"], keep_session=True)
            async def check_tags(event: a_event):
                return event.get_plaintext()
            
            async for resp in check_tags(timeout=240, retry=3,prompt="重试次数: {count}"):
                if resp is None or resp == "":
                    await upload.finish("请老师好好输入标签，不然日富美就生气啦！\n请老师从头再来!")
                if resp == "取消":
                    await upload.finish("已取消~")
                break
            
            i["tags"] = resp.split(" ")

        await upload.send("正在上传，请老师稍等...")

        for i in imgs:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f'{endpoint}/upload', json=i, headers={"Content-Type":"application/json"})
            if resp.text == "ok":
                await upload.send(f"已为老师上传第 {imgs.index(i)+1}/{len(imgs)} 张图片~")
            else:
                await upload.send(f"啊哈哈...第 {imgs.index(i)+1} 张图片上传失败！请在小窝内联系日富美的作者哦！\n日富美的小窝：976996605")
                await upload.send(f"错误信息：{resp.text}")

        await upload.finish("上传完毕！感谢老师的贡献呀~\n日富美的超管们审核完成后会在这里通知老师的！")


    @staticmethod
    async def upload_event_group(upload: Matcher, bot: Bot, event: GroupMessageEvent):
        await upload_setu.__upload_event__(upload, bot, event)
        
    @staticmethod
    async def upload_event_private(upload: Matcher, bot: Bot, event: PrivateMessageEvent):
        await upload_setu.__upload_event__(upload, bot, event)


class send_result:
    @staticmethod
    async def clear(clear: Matcher):
        async with httpx.AsyncClient() as client:
            await client.get(f'{endpoint}/audit/clear_result')
        await clear.finish("清空完成~")
    
    @staticmethod
    async def send_result_event(send_result: Matcher, bot: Bot):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{endpoint}/audit/get_result', headers={"Content-Type":"application/json"})
        data = json.loads(resp.text)

        for img in data["smash"]:
            # 审核不通过的图片

            if int(bot.self_id) != img["bot_id"]:
                continue
            
            uid = img["uid"]
            gid = img["gid"]
            result = await check_image(f"https://proxy.wstudio.work/https://img.wstudio.work//hifumi-wrsetu-banned/{img['name']}", uid)    # 进行内容审查，这里特地加了代理，否则会超时
            if result[0]:
                # 正常
                message = f"老师！您上传的色图没有通过！\n经过本日富美的审核...很有可能是因为标签没有打好！！\n您上传的图片："+MessageSegment.image(await download_url(f"https://img.wstudio.work//hifumi-wrsetu-banned/{img['name']}"))
                if gid == 0:
                    await bot.send_private_msg(user_id=uid, message=message)
                else:
                    await bot.send_group_msg(group_id=gid, message=
                        MessageSegment.at(uid)
                        +" "+message
                    )
            else:
                # 不合规
                message = f"老师！！！您上传的色图没有通过！\n并且通过日富美的审核，这张图片属于违规内容（涉及政治，暴力血腥，二维码等），被瓦尔基里看见是要被抓进去的！\n您上传的图片：https://img.wstudio.work//hifumi-wrsetu-banned/{img['name']}\n日富美的审核结果：{result[1]}"
                if gid == 0:
                    await bot.send_private_msg(user_id=uid, message=message)
                else:
                    await bot.send_group_msg(group_id=gid, message=
                        MessageSegment.at(uid)
                        +" "+message
                    )
            await send_result.send(f"已通知一张未通过的图片：\n上传者信息：\n   qq号:{hide_id(uid)}\n   群号:" + (hide_id(gid) if gid != 0 else "（私聊上传）") + f"\n图片信息：\n   图片id:{img['name']}")
                    
        for img in data["pass"]:
            # 审核通过了的

            if int(bot.self_id) != img["bot_id"]:
                continue
            
            uid = img["uid"]
            gid = img["gid"]
            message = f"老师！您上传的色图已经通过审核啦！感谢您做的贡献~\n您上传的图片："+MessageSegment.image(await download_url(f"https://img.wstudio.work//hifumi-wrsetu/{img['name']}"))+"\n标签："+str(img["tags"])
            if gid == 0:
                await bot.send_private_msg(user_id=uid, message=message)
            else:
                await bot.send_group_msg(group_id=gid, message=MessageSegment.at(uid)+" "+message)
            await send_result.send(f"已通知一张通过了的图片：\n上传者信息：\n   qq号:{hide_id(uid)}\n   群号:" + (hide_id(gid) if gid != 0 else "（私聊上传）") + f"\n图片信息：\n   图片id:{img['name']}")

        await send_result.finish(f"通知完毕~\n已通知审核通过的图片张数：{len(data['pass'])}\n已通知退回的图片张数：{len(data['smash'])}")

class setu:
    @staticmethod
    async def __setu_event__(setu: Matcher, event: GroupMessageEvent|PrivateMessageEvent, bot: Bot, args: Message = CommandArg()):
        if arg := args.extract_plain_text():
            tag = arg.split(" ")[0]
            if len(arg.split(" ")) > 1:
                count = int(arg.split(" ")[1])
                if count > 5:
                    await setu.finish("老师！不要太贪心啦，一次最多获取5张哦！")
            else:
                count = 1
            if len(arg.split(" ")) > 2:
                if arg.split(" ")[2] == "r18":
                    if isinstance(event, GroupMessageEvent):
                        if not get_r18(event.group_id):
                            await setu.finish("老师，这里不允许色色哦！请呼叫管理员或群主开启！")
                    r18 = True
            else:
                r18 = False

            data = {
                "tag": tag,
                "count": count,
                "r18": r18
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(f'{endpoint}/setu', json=data, headers={"Content-Type":"application/json"})
            resp = json.loads(resp.text)

            if not resp["data"]:
                # 没有图片
                await setu.finish("没有找到图片，老师可以上传几张哦！")

            forward_messages = []

            if r18:
                # r18图片使用聊天记录合并转发

                for i in resp["data"]:
                    forward_messages.append(
                        MessageSegment(
                            type="node",
                                data={
                                    "user_id": str(event.self_id),
                                    "nickname": "Hifumi_Setu",
                                    "name": "Hifumi_Setu",
                                    "uin": str(event.self_id),
                                    "content": MessageSegment.image(await download_url(i["url"])),
                                }
                        )
                    )

                if isinstance(event,GroupMessageEvent):
                    await bot.send_group_forward_msg(group_id=event.group_id, messages=forward_messages)
                elif isinstance(event,PrivateMessageEvent):
                    await bot.send_private_msg(user_id=event.user_id, message=forward_messages)
            else:
                for i in resp["data"]:
                    await setu.send(MessageSegment.image(await download_url(i["url"])))
                
            if len(resp) < count:
                await setu.finish("老师，只有这几张了哦！老师可以上传几张～")
        else:
            await setu.finish("请老师输入一个标签！")
            
    @staticmethod
    async def setu_event_group(setu_matcher: Matcher, event: GroupMessageEvent, bot: Bot, args: Message = CommandArg()):
        await setu.__setu_event__(setu_matcher, event, bot, args)
        
    @staticmethod
    async def setu_event_private(setu_matcher: Matcher, event: PrivateMessageEvent, bot: Bot, args: Message = CommandArg()):
        await setu.__setu_event__(setu_matcher, event, bot, args)

class size:
    @staticmethod
    async def size_event(size: Matcher):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'{endpoint}/size', headers={"Content-Type":"application/json"})
        data = json.loads(resp.text)
        await size.finish(f"当前图库总数：{data['size']}")
        
class r18:
    @staticmethod
    async def enable(r18: Matcher, event: GroupMessageEvent):
        set_r18(True, event.group_id)
        await r18.finish("已开启r18，不要让小春同学看到哦❤")
        
        
    @staticmethod
    async def disable(r18: Matcher, event: GroupMessageEvent):
        set_r18(False, event.group_id)
        await r18.finish("已关闭r18～")
        

