<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <img src="https://github.com/WStudioGroup/hifumi-plugins/blob/main/remove.photos-removed-background.png" width="200">
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# hifumi-plugin-setu

_✨ 日富美bot的上传色图插件，基于 NoneBot2 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/WStudioGroup/hifumi-plugin-setu.svg" alt="license">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

Hifumi-Bot（日富美bot）的专属插件，使用 NoneBot 2 框架

## 📖 介绍

上传色图至API，API后台审核通过后添加至图库，后面可以通过标签进行搜索，获取色图

## ⚙️ 配置

在插件目录的"api_server"文件夹中，修改config.json文件：
```
{
    "tokens": {
        "【密码】": "【用户名】"
    },
    "s3": {
        "endpoint_url": "【s3储存地址】",
        "access_key": "【s3储存ak】",
        "secret_key": "【s3储存sk】"
    },
    "mongodb_url": "【mongodb数据库地址】"
}
```

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| 配置项1 | 是 | 无 | 配置说明 |
| 配置项2 | 否 | 无 | 配置说明 |

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 获取图库色图 | 群员/好友 | 否 | 群聊/私聊 | 顾名思义 |
| 图库色图，上传 | 群员/好友 | 否 | 群聊/私聊 | 上传色图 |
| 图库大小 | 群员/好友 | 否 | 群聊/私聊 | 查看图库大小 |
| 图库色图，开启r18 | 管理员+ | 否 | 群聊 | 开启r18，使这个群内允许获取带有“r18”标签的色图 |
| 图库色图，关闭r18 | 管理员+ | 否 | 群聊 | 反之 |
| 发送色图审核通知 | 超级管理员 | 否 | 群聊 | 在API后台审核通过后需要执行此命令，来通知各位老师自己上传的色图是否通过 |
| 清空审核记录 | 超级管理员 | 否 | 群聊 | 发送完审核通知后 必 须 执 行 |

## 其他
### /setu
获取色图

参数：
| 参数名 | 类型 | 必填 | 说明 |
|:-----:|:----:|:----:|:----:|
| tag | str | 是 | 标签，暂不支持多个标签 |
| num | int | 否 | 获取图片的数量，默认为1 |
| r18 | bool | 否 | 是否获取r18图片，默认为False |

返回值：
| 返回值名 | 类型 | 说明 |
|:-----:|:----:|:----:|
| data | list | 色图列表 |

data格式：
| 参数名 | 类型 | 说明 |
|:-----:|:----:|:----:|
| url | str | 色图url |
| tags | str | 色图标签 |
| gid | int | 上传者所在的群号，私聊上传则为0 |
| uid | int | 上传者的QQ号 |
| time | str | 上传时间 |

### /audit/result
获取审核结果

返回值：
| 返回值名 | 类型 | 说明 |
|:-----:|:----:|:----:|
| pass | list | 已通过的色图列表 |
| smash | list | 违规的色图列表 |

pass和smash的格式同上方的data格式

### /audit/clear_result
清空审核结果

### /num
获取图库数量

返回值：
| 返回值名 | 类型 | 说明 |
|:-----:|:----:|:----:|
| num | int | 图库数量，而不是大小 |
