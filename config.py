import json, os

"""
配置文件读取和保存
sample:
{
    "serial_config": {
        "port": "COM3",
        "baudrate": 9600,
        "timeout": 1
    },
    "game_scroes": [
        {"score": 2000, "time": "2024-11-13 22:35:30"}
    ]
}
"""

def load_config() -> dict:
    """
    加载配置文件
    """
    config = {}
    # 判断当前程序文件路径下是否有 config.json 文件,有读取配置，没有创建
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            # 判断 CONFIG是否None，是否字典类型
            if config is None or not isinstance(config, dict):
                config = {}
    else:
        config = {}
    return config

def save_config(config: dict) -> None:
    """
    保存配置文件, 如果文件不存在则创建
    """
    with open("config.json", "w") as f:
        # 将config 转换为json格式，格式化好，写入 config.json 文件
        json.dump(config, f, indent=4)

