import time
from pygame.locals import *

class PlaneController:
    """
    飞机控制类, 控制飞机移动和射击
    """

    shoot_frequency: float = 5 # 每秒子弹射击频率限制（1-10）范围

    def __init__(self, shoot_frequency: float = 5):
        """
        初始化 设置默认参数 
        """

        self.shoot_frequency = shoot_frequency
        self.last_shoot_time = time.time()
        
    def to_up(self, plane):
        """
        向上移动，当按下 W 键 或控制器向前倾斜时，会执行此方法
        """
        plane.moveUp()

    def to_down(self, plane):
        """
        向下移动，当按下 S 键 或控制器向后倾斜时，会执行此方法
        """
        plane.moveDown()
    
    def to_left(self, plane):
        """
        向左移动，当按下 A 键 或控制器向左倾斜时，会执行此方法
        """
        plane.moveLeft()

    def to_right(self, plane):
        """
        向右移动，当按下 D 键 或控制器向右倾斜时，会执行此方法
        """
        plane.moveRight()
    
    def can_shoot(self) -> bool:
        shoot_interval = 1000 / self.shoot_frequency
        if (time.time() - self.last_shoot_time) < shoot_interval / 1000:
            return False
        self.last_shoot_time = time.time()
        return True
    
    def shoot(self, plane):
        """
        射击方法，当按键盘 space 键 或 按下控制器 A 或 B 键时，系统会调用此方法
        """
        if self.can_shoot():
            plane.shoot()
        
    def deal_key_event(self, key_pressed, plane) -> None:

        if  key_pressed[K_UP] or key_pressed[K_w]:
            self.to_up(plane)
        if  key_pressed[K_DOWN] or key_pressed[K_s]:
            self.to_down(plane)
        if  key_pressed[K_LEFT] or key_pressed[K_a]:
            self.to_left(plane)
        if  key_pressed[K_RIGHT] or key_pressed[K_d]:
            self.to_right(plane)
        if key_pressed[K_SPACE] or key_pressed[K_j]:
            self.shoot(plane)
    
    def xy_change(self, degreeX, degreeY, ab_key_pressed: bool, plane):

        if degreeX > 0:
            self.to_right(plane)
        elif degreeX < 0:
            self.to_left(plane)
        if degreeY > 0:
            self.to_up(plane)
        elif degreeY < 0:
            self.to_down(plane)
            
        if ab_key_pressed:
            self.shoot(plane)
