import requests,httpx

API_KEY = "mRoXqtWt2KbtGUvpQkFQX17K"
SECRET_KEY = "M0tmgjSd9uFzyW6P4bxHFHgOG7UDyJwE"
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

async def check_image(url: str, uid: int) -> list:
    """
    使用百度云api检查图片
    仅检查涉政内容

    参数:
        url(str): 图片链接
        uid(int): 用户id

    返回值:
        [bool,str]: [是否通过,提示]
    """
    
    checkpoint = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_access_token()
    
    payload=f"imgUrl={url}&strategyId=38184&userId={str(uid)}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.request("POST", checkpoint, headers=headers, data=payload)

    data = response.json()
    print(data)

    if data["conclusionType"] == 2:
        return [False,data["data"][0]["msg"]]
    return [True,""]
    

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))
