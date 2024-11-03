from nonebot import require
require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

def set_r18(value: bool, gid: int):
    """
    设置是否开启r18

    参数:
        value(bool): 是否开启
        gid(int): 群号
    """

    file = store.get_data_file("hifumi_setu_r18", str(gid)+".txt")
    with open(str(file), "w+") as f:
        f.write("y" if value else "n")
        
def get_r18(gid: int) -> bool:
    """
    获取是否开启r18

    参数:
        gid(int): 群号

    返回:
        bool: 是否开启
    """
    file = store.get_data_file("hifumi_setu_r18", str(gid)+".txt")
    if not file.exists():
        return False
    return True if file.read_text() == "y" else False
    