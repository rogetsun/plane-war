import queue
from plane_war import PlaneGame
from plane_controller import PlaneController
from serial_device import SerialData, SerialDevice
from config import load_config

# 主函数
if __name__ == "__main__":
    # 创建串口线程和游戏线程通信队列，队列长度为100，队列数据类型为 SerialData
    serial_data_queue: queue.Queue[SerialData] = queue.Queue(maxsize=100)
    # 读取配置文件
    config = load_config()
    # 创建飞机控制器
    plane_controller = PlaneController()
    # 创建游戏对象
    plane_game = PlaneGame(serial_data_queue, config, plane_controller)
    # 开始游戏
    plane_game.run()


