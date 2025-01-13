from machine import *
from time import sleep, sleep_us, sleep_ms
import machine, neopixel, time, utime, math

np = neopixel.NeoPixel(machine.Pin(12), 12)


# 定义led类
class led:

    def getColor(c):
        if c == 'g' or c == 'green':
            return (0, 50, 0)
        elif c == 'r' or c == 'red':
            return (50, 0, 0)
        elif c == 'b' or c == 'blue':
            return (0, 0, 50)
        elif c == 'w' or c == 'white':
            return (50, 50, 50)
        elif c == 'o' or c == 'orange':
            return (50, 33, 0)
        elif c == 'y' or c == 'yellow':
            return (50, 50, 0)
        elif c == 'c' or c == 'cyan':
            return (0, 50, 50)
        elif c == 'p' or c == 'puple':
            return (27, 0, 50)
        else:
            return (0, 0, 0)

    def on(*args,id):
        if len(args) <= 1:
            c = args[0]
            color = led.getColor(c)

            if (id is None) or id == '' or id == all:
                for i in range(12):
                    np[i-1] = color
                    np.write()

            else:
                np[id-1] = color
                np.write()

        else:
            r1 = args[0]
            g1 = args[1]
            b1 = args[2]
 
            if r1>255:
                r = 51
            else:
                r = int(r1/5)
                
            if g1>255:
                g = 51
            else:
                g = int(g1/5)
                
            if b1>255:
                b = 51
            else:
                b = int(b1/5)

            if (id is None) or id == '' or id == all:
                for i in range(12):
                    np[i-1] = (r, g, b)
                    np.write()

            else:
                np[id-1] = (r, g, b)
                np.write()
                
    def off(*args,id):
        
        if (id is not None and id != '') and id != all:
            np[id-1] = (0, 0, 0)
            np.write()

        else:
            for i in range(12):
                np[i-1] = (0,0,0)
                np.write()

#获取声音程序
# 声敏电阻传感数据模拟读取
dwqVal0 = ADC(Pin(13))
dwqVal0.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V

def get_loudness():
    val_list = []
    v = 0
    while v<5:
        val_x0 = dwqVal0.read()/4-435  # 0-4095
        val_list.append(val_x0)
        time.sleep(0.02)
        v+=1
    vol = sum(val_list)/len(val_list)
    
    if vol > 100:
        return 100
    elif vol < 0:
        return -1*vol
    else:
        return vol

#计时器
def timer_reset():
    
    start_time = time.time()
    return start_time

start_time = time.time()
def timer_get():
        
    end_time = time.time()
    total_time = end_time - start_time
    
    return total_time

class accel():
    global error
    error=[0,0,0]
    def __init__(self, addr=0x68):
        self.iic = SoftI2C(scl=Pin(22, Pin.IN, Pin.PULL_UP), sda=Pin(21, Pin.IN, Pin.PULL_UP)) # i2c通信
        self.addr = addr
        self.iic.start()
        sleep_ms(1)
        self.iic.writeto(self.addr, bytearray([107, 0]))
        sleep_ms(1)
        self.iic.writeto_mem(self.addr,0x19,b'\x07') #gyro 125hz
        sleep_ms(1)
        self.iic.writeto_mem(self.addr,0x1a,b'\x04')  #low filter 21hz
        sleep_ms(1)
        self.iic.writeto_mem(self.addr,0x1b,b'\x08') #gryo 500/s 65.5lsb/g
        sleep_ms(1)
        self.iic.writeto_mem(self.addr,0x1c,b'\x08') #acceler 4g ,8192lsb.g
        sleep_ms(1)
        
        self.iic.stop()
        
        # self.error_gy()
        

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def error_gy(self):
        sleep(3)
        global error
        error=[0,0,0]
        vals = {}
        for i in range(0,10):
            raw_ints = self.get_raw_values()
            vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
            vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
            vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
            error[0]= error[0]+vals["GyX"]
            error[1]= error[1]+vals["GyY"]
            error[2]= error[2]+vals["GyZ"]
            sleep_ms(8)
        error[1]=error[1]/10.0
        error[2]=error[2]/10.0
        error[0]=error[0]/10.0

    def get_values(self):
        global error
        vals = {}
        raw_ints = self.get_raw_values()
        vals["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["AcZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tmp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])-error[0]
        vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])-error[1]
        vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])-error[2]
        #vals["GyZ1"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # returned in range of Int16
        # -32768 to 32767

Kp=0.8 #比例增益支配率收敛到加速度计/磁强计
Ki=0.001 #积分增益支配率的陀螺仪偏见的衔接
halfT=0.004 #采样周期的一半
q0=1
q1=0
q2=0
q3=0; #四元数的元素 ,代表估计方向
exInt=0
eyInt=0
ezInt=0 #按比例缩小积分误差
def IMUupdate(gx,gy,gz,ax,ay,az):
    K=0.7
    a=[0,0,0,0,0,0,0,0]
    global Kp,Ki,halfT,q0,q1,q2,q3,exInt,eyInt,ezInt
    if ax!=0 or ay!=0 or az!=0: 
        norm=math.sqrt(ax*ax+ay*ay+az*az);
    ax=ax/norm; #单位化
    ay=ay/norm;
    az=az/norm;
    #估计方向的重力
    vx=2* (q1*q3-q0*q2 );
    vy=2* (q0*q1+q2*q3 );
    vz=q0*q0-q1*q1-q2*q2+q3*q3;
    #错误的领域和方向传感器测量参考方向之间的交叉乘积的总和
    ex= (ay*vz-az*vy );
    ey= (az*vx-ax*vz );
    ez= (ax*vy-ay*vx );
    #积分误差比例积分增益
    exInt=exInt+ex*Ki;
    eyInt=eyInt+ey*Ki;
    ezInt=ezInt+ez*Ki;
    #调整后的陀螺仪测量
    gx=gx+Kp*ex+exInt;
    gy=gy+Kp*ey+eyInt;
    gz=gz+Kp*ez+ezInt;
    #整合四元数率和正常化
    q0=q0+ (-q1*gx-q2*gy-q3*gz )*halfT;
    q1=q1+ (q0*gx+q2*gz-q3*gy )*halfT;
    q2=q2+ (q0*gy-q1*gz+q3*gx )*halfT;
    q3=q3+ (q0*gz+q1*gy-q2*gx )*halfT;
    #正常化四元
    norm=math.sqrt(q0*q0+q1*q1+q2*q2+q3*q3 );
    q0=q0/norm;
    q1=q1/norm;
    q2=q2/norm;
    q3=q3/norm;
    Pitch=math.asin (-2*q1*q3+2*q0*q2 )*57.3; #pitch ,转换为度数
    if -2*q1*q1-2*q2*q2+1!=0:
        Roll=math.atan ((2*q2*q3+2*q0*q1)/(-2*q1*q1-2*q2*q2+1) )*57.3; #rollv
    a[0]=Pitch
    a[1]=Roll
    if ay*ay+az*az!=0:
        a[2]=-math.atan(ax/math.sqrt(ay*ay+az*az))*57.2957795
    if ax*ax+az*az!=0:
        a[3]=math.atan(ay/math.sqrt(ax*ax+az*az))*57.2957795
    a[4]=gx
    a[5]=gy
    a[6]=gz
    a[0]=-K*Pitch-(1-K)*a[2]
    a[1]=K*Roll+(1-K)*a[3]
    return a

def degreeX():
    mpuModel = accel()
    degreeXY = mpuModel.get_values()
    degreeValList = IMUupdate(degreeXY["GyX"]/1.14319,degreeXY["GyY"]/1.14319,degreeXY["GyZ"]/1.14319,degreeXY["AcX"]/8192,degreeXY["AcY"]/8192,degreeXY["AcZ"]/8192)
    return degreeValList[2]

def degreeY():
    mpuModel = accel()
    degreeXY = mpuModel.get_values()
    degreeValList = IMUupdate(degreeXY["GyX"]/1.14319,degreeXY["GyY"]/1.14319,degreeXY["GyZ"]/1.14319,degreeXY["AcX"]/8192,degreeXY["AcY"]/8192,degreeXY["AcZ"]/8192)
    return degreeValList[3]

def accX():
    mpuModel = accel()
    degreeXY = mpuModel.get_values()
    degreeValList = IMUupdate(degreeXY["GyX"]/1.14319,degreeXY["GyY"]/1.14319,degreeXY["GyZ"]/1.14319,degreeXY["AcX"]/8192,degreeXY["AcY"]/8192,degreeXY["AcZ"]/8192)
    return degreeValList[4]

def accY():
    mpuModel = accel()
    degreeXY = mpuModel.get_values()
    degreeValList = IMUupdate(degreeXY["GyX"]/1.14319,degreeXY["GyY"]/1.14319,degreeXY["GyZ"]/1.14319,degreeXY["AcX"]/8192,degreeXY["AcY"]/8192,degreeXY["AcZ"]/8192)
    return degreeValList[5]

def accZ():
    mpuModel = accel()
    degreeXY = mpuModel.get_values()
    degreeValList = IMUupdate(degreeXY["GyX"]/1.14319,degreeXY["GyY"]/1.14319,degreeXY["GyZ"]/1.14319,degreeXY["AcX"]/8192,degreeXY["AcY"]/8192,degreeXY["AcZ"]/8192)
    return degreeValList[6]

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

# 判断是否摇晃
def is_shake():
    while True:
        pin22 = Pin(22, Pin.IN, Pin.PULL_UP)
        pin21 = Pin(21, Pin.IN, Pin.PULL_UP)
        i2c = SoftI2C(scl=pin22, sda=pin21) # i2c通信
        mpuModel = accel()
        mpuModel.error_gy()
        accel_dict = mpuModel.get_values()
        ax=accX()
        ay=accY()
        az=accZ()
        if -500>ax or ax>500 or -500>ay or ay>500 or -500>az or az>500:
            aFlag = 1
        else:
            aFlag = 0
        if aFlag==1 :
            return 1
        else:
            return 0
   
# 获取摇晃强度
def get_shakeval():
    while True:
        dList = [abs(accX()),abs(accY()),abs(accZ())]
        maxd = max(dList)/300
        extent = int(maxd)
        #print(extent)
        return extent
#print(get_shakeval())

#判断端口0是否被触摸
class pin0:
    def is_touch():
        touch_pin0 = TouchPad(Pin(2)) # 触摸按键功能引脚对象创建
        touch_value0 = touch_pin0.read()
        touchNumber = 200
        if touch_value0 < touchNumber:
                return 1
        else:
                return 0

    def get_touch():
        touch_pin0 = TouchPad(Pin(2)) # 触摸按键功能引脚对象创建
        touch_value0 = touch_pin0.read()
        if(touch_value0>100):
                touch_value0=(800-touch_value0)/70*2
        else:
                touch_value0=20+(100-touch_value0)/5*4
        if(touch_value0<0):
                return 0
        else:
                return touch_value0

#print(pin0.is_touch())
#print(pin0.get_touch())

#判断端口1是否被触摸
class pin1:
    def is_touch():
        touch_pin1 = TouchPad(Pin(15)) # 触摸按键功能引脚对象创建
        touch_value1 = touch_pin1.read()
        touchNumber = 200
        if touch_value1 < touchNumber:
                return 1
        else:
                return 0
    def get_touch():
        touch_pin1 = TouchPad(Pin(15)) # 触摸按键功能引脚对象创建
        touch_value1 = touch_pin1.read()
        if(touch_value1>100):
                touch_value1=(800-touch_value1)/70*2
        else:
                touch_value1=20+(100-touch_value1)/5*4
        if(touch_value1<0):
                return 0
        else:
                return touch_value1
#print(pin1.is_touch())
#print(pin1.get_touch())

#判断端口2是否被触摸
class pin2:
    def is_touch():
        touch_pin2 = TouchPad(Pin(14)) # 触摸按键功能引脚对象创建
        touch_value2 = touch_pin2.read()
        touchNumber = 200
        if touch_value2 < touchNumber:
                return 1
        else:
                return 0
    def get_touch():
        touch_pin2 = TouchPad(Pin(14)) # 触摸按键功能引脚对象创建
        touch_value2 = touch_pin2.read()
        if(touch_value2>100):
                touch_value2=(800-touch_value2)/70*2
        else:
                touch_value2=20+(100-touch_value2)/5*4
        if(touch_value2<0):
                return 0
        else:
                return touch_value2
#print(pin2.is_touch())
#print(pin2.get_touch())

#判断端口3是否被触摸
class pin3:
    def is_touch():
        touch_pin3 = TouchPad(Pin(27)) # 触摸按键功能引脚对象创建
        touch_value3 = touch_pin3.read()
        touchNumber = 200
        if touch_value3 < touchNumber:
                return 1
        else:
                return 0
    def get_touch():
        touch_pin3 = TouchPad(Pin(27)) # 触摸按键功能引脚对象创建
        touch_value3 = touch_pin3.read()
        if(touch_value3>100):
                touch_value3=(800-touch_value3)/70*2
        else:
                touch_value3=20+(100-touch_value3)/5*4
        if(touch_value2<0):
                return 0
        else:
                return touch_value2
#print(pin3.is_touch())
#print(pin3.get_touch())

#判断是否左倾
def is_tiltleft():
    if get_roll()<0:
        return 1
    return 0

#判断是否右倾
def is_tiltright():
    if get_roll()>0:
        return 1
    return 0

#判断是否上斜
def is_arrowup():
    if get_pitch()>0:
        return 1
    return 0

#判断是否下斜
def is_arrowdown():

    if get_pitch()<0:
        return 1
    return 0

#获取翻滚角
def get_roll():
    pin22 = Pin(22, Pin.IN, Pin.PULL_UP)
    pin21 = Pin(21, Pin.IN, Pin.PULL_UP)
    i2c = SoftI2C(scl=pin22, sda=pin21) # i2c通信
    mpuModel = accel()
    mpuModel.error_gy()
    accel_dict = mpuModel.get_values()
    degreeValList = IMUupdate(accel_dict["GyX"]/1.14319,accel_dict["GyY"]/1.14319,accel_dict["GyZ"]/1.14319,accel_dict["AcX"]/8192,accel_dict["AcY"]/8192,accel_dict["AcZ"]/8192)
    roll = degreeValList[1];
    print(roll)
    return roll

#获取俯仰角
def get_pitch():
    pin22 = Pin(22, Pin.IN, Pin.PULL_UP)
    pin21 = Pin(21, Pin.IN, Pin.PULL_UP)
    i2c = SoftI2C(scl=pin22, sda=pin21) # i2c通信
    mpuModel = accel()
    mpuModel.error_gy()
    accel_dict = mpuModel.get_values()
    degreeValList = IMUupdate(accel_dict["GyX"]/1.14319,accel_dict["GyY"]/1.14319,accel_dict["GyZ"]/1.14319,accel_dict["AcX"]/8192,accel_dict["AcY"]/8192,accel_dict["AcZ"]/8192)
    pitch = degreeValList[0];
    print(pitch)
    return pitch

#判断触摸按键是否被按下
def is_pressA():
        btnA = Pin(25, Pin.IN, Pin.PULL_DOWN)
        if btnA.value()==1 :
            return 1
        return 0
    
def is_pressB():
        btnB = Pin(10, Pin.IN, Pin.PULL_DOWN)
        if btnB.value()==1:
            return 1
        return 0
