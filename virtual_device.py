import serial
import time
import random

class VirtualDevice:
    """
    虚拟设备类，用于模拟真实设备，产生数据，通过串口发送
    """
    def __init__(self, port: str, baudrate: int):
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.log(f"虚拟设备实例创建成功，串口: {port}, 波特率: {baudrate}")
    
    def run(self):
        """主循环"""
        self.log("虚拟设备启动，开始模拟数据发送...")
        
        while True:
            # 接收请求
            try:
                # 模拟发送数据
                data = self.generate_data()
                self.serial.write(data)
                self.log(f"发送数据: {data}")
                # 延时，模拟人类操作时间间隔，人类正常连续按键两次的时间间隔为0.18秒上下,生成随机 0.18 上下的延时
                sleep_time = random.uniform(0.10, 0.38)
                time.sleep(sleep_time)
                
            except Exception as e:
                self.log(f"错误: {str(e)}")
                time.sleep(0.1)  # 发生错误时等待较长时间，避免频繁重试
        
    
    def generate_data(self) -> bytes:
        """模拟生成数据，格式："""
        
        # X轴角度：-90到90度
        mpuX = random.uniform(-90, 90)
        
        # Y轴角度：-90到90度
        mpuY = random.uniform(-90, 90)
        
        # 按钮状态：0或1
        btnA = random.randint(0, 1)
        btnB = random.randint(0, 1)
        
        # 按指定格式生成数据字符串
        data = f"mpuX:{mpuX:.2f},mpuY:{mpuY:.2f},btnA:{btnA:.0f},btnB:{btnB:.0f}\n"
        
        return data.encode()


    def close(self):
        """关闭串口"""
        if self.serial.is_open:
            self.serial.close()

    # 打印日志，可以接受和print一样的参数
    def log(self, *msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]", *msg)
    
# 使用示例
if __name__ == "__main__":
    virtual_device = None
    try:
        # 命令行和用户交互，输入串口参数
        port = input("请输入串口: ")
        baudrate = int(input("请输入波特率: "))
        print(f"创建虚拟设备实例，串口: {port}, 波特率: {baudrate}")
        virtual_device = VirtualDevice(port=port, baudrate=baudrate)
        # 运行虚拟设备
        virtual_device.run()
    except KeyboardInterrupt:
        virtual_device.log("\n程序被用户中断")
    finally:
        if virtual_device:
            virtual_device.close()
            virtual_device.log("虚拟设备关闭")
    print("程序退出")
    exit(0)
    