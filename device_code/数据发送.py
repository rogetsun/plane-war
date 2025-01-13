from machine import Pin, UART
import time
from tltcode import *

# 初始化NeoPixel灯带
n = 12  # 灯带上的LED数量
p = 12  # 灯带控制GPIO
np = neopixel.NeoPixel(Pin(p), n)
lightNum = 100

# 板载2个按键测试
btnL = Pin(10, Pin.IN, Pin.PULL_DOWN)
btnR = Pin(25, Pin.IN, Pin.PULL_DOWN)

# 初始化串口对象，波特率为115200
uart = UART(1, baudrate=115200, rx=3, tx=1)

# 模拟传感器读取函数
def read_mpuX():
    return degreeX()

def read_mpuY():
    return degreeY()

def read_btnA():
    return btnL.value()

def read_btnB():
    return btnR.value()

# 读取并发送传感器数据
def send_sensor_data():
    mpuX = read_mpuX()
    mpuY = read_mpuY()
    btnA = read_btnA()
    btnB = read_btnB()
    
    data = "mpuX:{:.2f},mpuY:{:.2f},btnA:{:.0f},btnB:{:.0f}".format(mpuX, mpuY, btnA, btnB)
    uart.write(data + '\n')


while True:
    # 发送传感器数据
    send_sensor_data()
    
    # 每秒发送一次传感器数据
    time.sleep(0.2)




