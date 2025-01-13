import serial
import queue
import threading
import time


class SerialData():
    """
        串口数据类
    """
    data : str

    mpu_x : float = 0
    mpu_y : float = 0
    btn_a : bool = False
    btn_b : bool = False

    def __init__(self, data: bytes):
        """
            初始化串口数据
        """
        self.data = data.decode().strip()
        self.parse_data()
        
    
    def parse_data(self):
        """解析数据
        f"mpuX:{mpuX:.2f},mpuY:{mpuY:.2f},btnA:{btnA:.0f},btnB:{btnB:.0f}\n"
        """
        data = self.data.split(",")
        for item in data:
            key, value = item.split(":")
            if key == "mpuX":
                self.mpu_x = float(value)
            elif key == "mpuY":
                self.mpu_y = float(value)
            elif key == "btnA":
                self.btn_a = bool(float(value))
            elif key == "btnB":
                self.btn_b = bool(float(value))
        


class SerialDevice(threading.Thread):
    """
        串口设备类，继承线程类，可以启动线程读取数据
        参数：
            port: 串口名称或设备路径
            baudrate: 波特率
            timeout: 超时时间
            serial_data_queue: 串口数据队列
        介绍：
            打开串口，收到数据后会 创建 SerialData 对象, 
    """

    ser: serial.Serial = None
    port: str = ""
    baudrate: int = 9600
    timeout: int = 1
    serial_data_queue: queue.Queue[SerialData] = None
    daemon : bool = True
    running: bool = False

    def __init__(self, serial_data_queue: queue.Queue[SerialData], port, baudrate, timeout=1):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_data_queue = serial_data_queue
        self.connect()
        self.running = True

    def run(self):
        """
            线程运行函数，读取串口数据并放入队列
        """
        print(f"串口设备线程开始运行, 串口: {self.ser}")
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    data = self.ser.readline()
                    serial_data = None
                    try:
                        serial_data = SerialData(data)
                    except Exception as e:
                        # 解析数据失败，就算readline，依然有小爱概率串口数据错误，粘包、半包等问题，这里直接丢弃
                        # 如果更严谨，可以考虑修改和设备的通信协议，不用字符串的 bytes，换用固定字节长度字节+crc校验，
                        # 一个开始字节0x55 + 2 个 float角度值 + 2 个 bool按键值放一个字节 2 位 + 1 字节校验位 + 1 字节结束字节0xaa
                        print(f"解析串口数据失败: {e}, 丢弃数据")
                        continue
                    
                    if serial_data:
                        self.serial_data_queue.put(serial_data)
                else:
                    time.sleep(0.01)
            except queue.Full:
                pass
            except Exception as e:
                print(f"读取串口数据失败: {e}")
                break

        if self.ser and self.ser.is_open:
            self.close()

    def connect(self):
        """
            连接串口
        """
        try:
            if not self.ser or not self.ser.is_open:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                print(f"串口连接成功: {self.ser.name}")
        except serial.SerialException as e:
            print(f"串口连接失败: {e}")
            
            
    def close(self):
        """
            关闭串口
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
        self.running = False
        print(f"串口设备线程关闭, 串口: {self.ser}")

    def clear_serial(self):
        """
            清空串口数据
        """
        self.serial_data_queue.queue.clear()
        if self.ser:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

if __name__ == '__main__':
    # 打印所有可用串口
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"{port.device} - {port.description}")
    