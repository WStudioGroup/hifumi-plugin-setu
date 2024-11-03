from flask import Flask, request, render_template, send_from_directory
from flask_socketio import SocketIO
import mongodb
import utils
import json
import random

__debugging__ = False    # 调试模式，将不会上传图片和插入数据库
app = Flask(__name__)
socketio = SocketIO(app)
tokens = {}             # 登录用户
imgs_to_audit = []      # 待审核图片
"""
{
    "name": "1.jpg",
    "url": "http://.../1.jpg",
    "tags": ["1", "2", "3"],
    "uid": "12345678",
    "gid": "12345678",
    "time": "2023-01-01 00:00:00"
}
"""
imgs_to_sumbit = []     # 即将上传的图片

imgs_passed = []        # 通过了的图片，
                        # 和imgs_to_sumbit不同
                        # 前者在提交完毕后将会清空
                        # 而此变量将会一直保留到 /audit/clear_result 请求
"""
同上
"""
imgs_to_smash = []      # 违规图片

# 座右铭嘿嘿嘿
@app.route("/")
def index():
    msg = "志纳万技，臻于至善<br>\nAspire to Master All Skills, Strive for Perfection<br>\n—— WR"
    return render_template("text.html", text=msg)

# 后台登录界面
@app.route("/login/<token>")
def login(token: str):
    global tokens, imgs_to_audit, imgs_to_sumbit, imgs_to_smash

    if token not in tokens:
        return render_template("text.html", text="不正确的token，登录失败")
    
    if not imgs_to_audit:
        # 无待审核图片
        if imgs_to_sumbit or imgs_to_smash:
            # 有待上传图片
            return render_template("login.html",ready_to_sumbit="已准备好提交",sumbitable="True")
        return render_template("text.html", text="没有待审核图片，请等待~")
    
    img = random.choice(imgs_to_audit)
    return render_template("login.html", 
        username=tokens[token],
        img_url=img["url"],
        img_tags=img["tags"],
        ready_to_sumbit="未审核完毕，暂时不能提交",
        sumbitable="False"
    )

# 上传新图片
@app.route("/upload", methods=["POST"])
async def upload():
    global imgs_to_audit

    data = request.get_json()
    img_url = data["url"]
    await utils.download_img(img_url, data["name"])    # 缓存文件
    data["url"] = "get_temp/"+data["name"]             # 替换文件路径，让前端访问时获取的是服务器缓存的文件
    imgs_to_audit.append(data)

    return "ok"

# 审核通过接口
@app.route("/audit/pass", methods=["POST"])
def audit_pass():
    global imgs_to_audit, imgs_to_sumbit

    img = request.get_json()["img_name"]
    for i in imgs_to_audit:
        if i["name"] == img:
            # 将数据从待审核列表移除，并添加进待上传列表
            imgs_to_sumbit.append(i)
            imgs_to_audit.remove(i)
            print("pass")
            break
    return "ok"

# 审核不通过接口
@app.route("/audit/smash", methods=["POST"])
def audit_smash():
    global imgs_to_audit, imgs_to_smash

    img = request.get_json()["img_name"]
    for i in imgs_to_audit:
        if i["name"] == img:
            # 将数据从待审核列表移除，并添加进违规列表
            imgs_to_smash.append(i)
            imgs_to_audit.remove(i)
            break
    return "ok"

# 提交上传图片
@app.route("/audit/sumbit", methods=["POST"])
def sumbit():
    global imgs_to_sumbit, imgs_to_smash, imgs_passed, __debugging__

    uploaded = 0    # 已上传的图片数量
    socketio.emit('update_upload_progress', 
        f"{uploaded}/{len(imgs_to_sumbit)}", 
        namespace='/upload'
    )   # 初始化上传进度
    for i in imgs_to_sumbit:
        # 审核通过的图片
        if not __debugging__:
            mongodb.insert(i["name"], i["tags"], i["uid"], i["gid"])        # 插入数据库
            utils.upload(i["name"])                                         # 上传图片
        socketio.emit('update_upload_progress', 
            f"{uploaded}/{len(imgs_to_sumbit)}", 
            namespace='/upload'
        )   # 更新上传进度
        uploaded += 1

    for i in imgs_to_smash:
        # 不通过的图片
        """
        别问我为什么不通过的图片也要上传
        问就是qq的链接会过期,懒得喷
        后面再加个清空的函数就行了
        """
        utils.upload(i["name"],banned=True) # 上传图片

    imgs_passed = imgs_to_sumbit
    imgs_to_sumbit = []
    # 使用websocket通知前端
    socketio.emit('upload_complete', {}, namespace='/upload')

    utils.clear_directory("temp")   # 清除图片缓存

    return "ok"
@socketio.on('connect', namespace='/upload')
def connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/upload')
def disconnect():
    print('Client disconnected')


# 获取审核结果
@app.route("/audit/get_result")
def audit_result():
    global imgs_passed, imgs_to_smash

    return json.dumps({
        "pass": imgs_passed,
        "smash": imgs_to_smash
    })

# 清除审核结果
@app.route("/audit/clear_result")
def audit_clear_result():
    global imgs_to_sumbit, imgs_to_smash, imgs_to_audit

    imgs_to_sumbit = []
    imgs_to_smash = []
    imgs_to_audit = []

    utils.clear_directory("temp")   # 清除图片缓存

    return "ok"

# 获取缓存的文件
@app.route("/login/get_temp/<filename>")
def get_img(filename: str):
    return send_from_directory("temp", filename)

# 获取图库数量
@app.route("/size")
def get_size():
    return json.dumps({"size": mongodb.get_images_length()})

# 获取色图
@app.route("/setu", methods=["POST","GET"])
def setu():
    global cdn

    data = request.get_json()
    tag = data["tag"]
    count = data["count"]
    r18 = data["r18"]

    imgs = mongodb.search_by_keyword(tag, count, r18)
    
    return json.dumps({"data":imgs})

if __name__ == '__main__':
    with open("config.json", "r") as f:
        data = json.loads(f.read())
        tokens = data["tokens"]
        mongodb.mongodb_url = data["mongodb_url"]

    mongodb.init()          # 连接数据库
    try:
        app.run(host='0.0.0.0', port=5264)
    except KeyboardInterrupt:
        # 捕捉退出信号
        mongodb.close()                 # 关闭数据库连接
        utils.clear_directory("temp")   # 清除图片缓存