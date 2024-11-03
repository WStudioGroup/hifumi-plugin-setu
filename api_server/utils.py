import boto3
from botocore.config import Config
import httpx
import json

# 定义 endpoint、access key 和 secret key
endpoint_url = ""
access_key = ""
secret_key = ""
with open("config.json", "r") as f:
    data = json.loads(f.read())
    endpoint_url = data["s3"]["endpoint_url"]
    access_key = data["s3"]["access_key"]
    secret_key = data["s3"]["secret_key"]
# 创建 S3 客户端实例并指定 endpoint 和凭证信息
s3 = boto3.client('s3',
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    verify=True,
    config=Config(proxies={'https': '127.0.0.1:7890'})
)

proxies={'http://': 'http://127.0.0.1:7890', 'https://': 'http://127.0.0.1:7890'}

async def download_url(url: str) -> bytes:
    """
    下载文件
    最多重试三次
    
    参数:
        url(str): 文件链接
    
    返回:
        bytes: 文件二进制数据
    """
    async with httpx.AsyncClient(proxies=proxies) as client:
        for i in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                print(f"Error downloading {url}, retry {i}/3: {str(e)}")

async def download_img(url, filename) -> str:
    """
    缓存图片至本地

    参数:
        url(str):       图片链接
        filename(str):  图片名称
    
    返回:
        str: 图片名称
    """
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                with open("temp/"+filename, 'wb') as f:
                    f.write(resp.content)
                    return filename
            except Exception as e:
                print(f"Error downloading {url}, retry {i}/3: {str(e)}")
                return ""

def upload(img, banned=False) -> str:
    """
    上传文件
    
    参数:
        img(str): 图片名称
        banned(bool): 是否为不合规图片
    
    返回:
        str: 图片链接
    """

    try:
        bucket_name = 'hifumi-wrsetu'
        # 上传文件
        local_file_path = 'temp/'+img  # 本地文件路径
        
        # S3中的文件名，可以包括文件夹
        if not banned:
            s3_file_key = '/hifumi-wrsetu/' + img
        else:
            s3_file_key = '/hifumi-wrsetu-banned/' + img
            
        s3.upload_file(local_file_path, bucket_name, s3_file_key)
        return f"https://img.wstudio.work//hifumi-wrsetu/{img}"
    except Exception as ex:
        print(str(ex))
        return ""
    
import requests

API_KEY = "mRoXqtWt2KbtGUvpQkFQX17K"
SECRET_KEY = "M0tmgjSd9uFzyW6P4bxHFHgOG7UDyJwE"

def check_image(img:str) -> bool:
    """
    检测图片（不检测色情）

    参数:
        img(str): 图片链接

    返回值:
        bool: 是否通过
    """
        
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_access_token()
    
    payload=f'imgUrl={img.replace("/","%2F")}&strategyId=38187'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()

    print(str(data))

    if data["conclusionType"] == 2:
        return True
    return False
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


import os, shutil

def clear_directory(directory):
    """
    删除某个文件夹下的所有文件

    参数:
        directory(str): 文件夹路径
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或链接
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除目录及其所有内容
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
