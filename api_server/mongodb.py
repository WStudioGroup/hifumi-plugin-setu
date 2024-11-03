from pymongo import MongoClient
import random,time

mongodb_url = ""
cdn = "https://img.wstudio.work//hifumi-wrsetu/"

def init():
    """
    初始化（连接数据库）
    """
    global mongodb_url, client
    client = MongoClient(mongodb_url) 

def get_images_length() -> int:
    global client

    client = MongoClient(mongodb_url)
    db = client['WrSetu_API']
    collection = db['images']
    client = MongoClient(mongodb_url)
    return collection.count_documents({})

def search_by_keyword(keyword: str, count: int, r18: bool) -> list:
    """
    使用关键词搜索
    
    参数:
        keyword(str): 关键词
        count(int):   数量
        r18(bool):     是否搜索r18

    返回值:
        list: 图片列表
    """
    global client

    result = []
    db = client['WrSetu_API']
    collection = db['images']
    if r18:
        query = {
            'tags': {
                '$all': [keyword, "r18"]
            }
        }
    else:
        query = {
            'tags': {
                '$all': [keyword],
                "$nin": ["r18"]
            }
        }
    data = list(collection.find(query))
    if data:
        imgs = []
        for i in data:
            img = {
                "url": cdn+i["img"],
                "tags": list(i["tags"]),
                "gid": i["uploader"]["gid"],
                "uid": i["uploader"]["uid"],
                "time": i["time"]
            }
            imgs.append(img)

        index = 0
        while index < count:
            img = random.choice(imgs)
            for i in result:
                if i["url"] == img["url"]:
                    # 随机到了重复的图片，继续随机
                    continue
            result.append(img)
            if index >= len(imgs):
                break
            index += 1

        random.shuffle(result)      # 随机打乱

        return result
    else:
        return []

def insert(img: str, tags: list, uid: int, gid: int):
    """
    添加新图片

    参数:
        img(str):   图片名称
        tags(list): 标签列表
        uid(int):   上传者QQ号
        gid(int):   群号,私聊上传则为0
    """
    global client

    client = MongoClient(mongodb_url)
    db = client['WrSetu_API']
    collection = db['images']
    document = {
        "tags": tags,
        "uploader": {
            "uid": uid,
            "gid": gid
        },
        "img": img,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    }
    # 插入文档
    result = collection.insert_one(document)

    # 打印插入结果的ID
    print('Document inserted with ID:', result.inserted_id)

def close():
    """
    断开数据库连接
    """
    global client
    client.close()
