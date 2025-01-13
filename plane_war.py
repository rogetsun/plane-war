# 设置文件字符集
# coding: utf-8

import pygame           # 导入pygame库
from pygame.locals import *  # 导入pygame库中的一些常量
from sys import exit  # 导入sys库中的exit函数
import random, queue, time, platform, os, sys
from config import save_config
from serial_device import SerialData, SerialDevice
from plane_controller import PlaneController
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return False
                    
    def draw(self, screen):
        txt_surface = self.font.render(self.text, True, self.color)
        width = max(200, txt_surface.get_width()+10)
        self.rect.w = width
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(txt_surface, (self.rect.x+5, self.rect.y+5))

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('dodgerblue2')
        self.text = text
        self.font = pygame.font.Font(None, 32)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        txt_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = txt_surface.get_rect(center=self.rect.center)
        screen.blit(txt_surface, text_rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, init_pos, bullet_img=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img or pygame.image.load(get_resource_path('resources/image/bullet.png')).convert_alpha()  
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 12

    def move(self):
        self.rect.top -= self.speed
        


class Player(pygame.sprite.Sprite):
    def __init__(self, init_pos, plane_controller: PlaneController):
        pygame.sprite.Sprite.__init__(self)
        self.plane_controller = plane_controller

        player_img01= pygame.image.load(get_resource_path('resources/image/player1.png'))
        player_img02= pygame.image.load(get_resource_path('resources/image/player2.png'))
        player_img03= pygame.image.load(get_resource_path('resources/image/player_off1.png'))
        player_img04= pygame.image.load(get_resource_path('resources/image/player_off2.png'))
        player_img05= pygame.image.load(get_resource_path('resources/image/player_off3.png'))
        self.player_img1 = pygame.transform.scale(player_img01, (74.4,76.8)).convert_alpha()
        self.player_img2 = pygame.transform.scale(player_img02, (74.4,76.8)).convert_alpha()
        self.player_img3 = pygame.transform.scale(player_img03, (74.4,76.8)).convert_alpha()
        self.player_img4 = pygame.transform.scale(player_img04, (74.4,76.8)).convert_alpha()
        self.player_img5 = pygame.transform.scale(player_img05, (74.4,76.8)).convert_alpha()

        self.image = [self.player_img1, self.player_img2, self.player_img2, self.player_img3, self.player_img4, self.player_img5]
        self.rect = self.player_img1.get_rect()
        self.rect.topleft = init_pos  
        self.speed = 8  
        self.bullets = pygame.sprite.Group()  
        self.img_index = 0  
        self.is_hit = False  
        self.mask = pygame.mask.from_surface(self.image[0])

    def deal_serial_data(self, serial_data_list: list[SerialData]):
        if serial_data_list and len(serial_data_list) > 0:
            for serial_data in serial_data_list:
                ab_key_pressed = serial_data.btn_a or serial_data.btn_b
                self.plane_controller.xy_change(serial_data.mpu_x, serial_data.mpu_y, ab_key_pressed, self)


    def move(self, x_distance, y_distance):
        if self.is_hit:
            return
        self.rect.left += x_distance
        self.rect.top += y_distance
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def shoot(self):
        self.bullets.add(Bullet(self.rect.midtop))

    def moveUp(self, dis = None):
        self.move(0, -self.speed if dis is None else dis)

    def moveDown(self, dis = None):
        self.move(0, self.speed if dis is None else dis)

    def moveLeft(self, dis = None):
        self.move(-self.speed if dis is None else dis, 0)

    def moveRight(self, dis = None):
        self.move(self.speed if dis is None else dis, 0)


class Enemy(pygame.sprite.Sprite):
    """
    敌机类
    """
    def __init__(self, init_pos=None):
        pygame.sprite.Sprite.__init__(self)

        self.enemy_img1= pygame.image.load(get_resource_path('resources/image/enemy1.png')).convert_alpha()
        self.enemy_img2= pygame.image.load(get_resource_path('resources/image/enemy2.png')).convert_alpha()
        self.enemy_img3= pygame.image.load(get_resource_path('resources/image/enemy3.png')).convert_alpha()
        self.enemy_img4= pygame.image.load(get_resource_path('resources/image/enemy4.png')).convert_alpha()

        self.image = self.enemy_img1
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos if init_pos else [0, 0]

        self.down_imgs = [self.enemy_img1, self.enemy_img2, self.enemy_img3, self.enemy_img4]
        # 敌机移动速度
        self.speed = 2
        # 敌机爆炸图片索引
        self.down_index = 0
        self.mask = pygame.mask.from_surface(self.image)

    # 敌机移动，边界判断及删除在游戏主循环里处理
    def move(self):
        self.rect.top += self.speed

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def set_pos(self, pos):
        self.rect.topleft = pos

class PlaneGame:
    def __init__(self, serial_data_queue: queue.Queue[SerialData], config: dict, plane_controller: PlaneController):

        self.serial_thread = None
        self.serial_data_queue: queue.Queue[SerialData] = serial_data_queue
        self.config = config
        self.plane_controller = plane_controller

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('飞机大战')
        ic_launcher = pygame.image.load(get_resource_path('resources/image/plane.png')).convert_alpha()
        pygame.display.set_icon(ic_launcher)
        bc = pygame.image.load(get_resource_path('resources/image/bc.jpg'))
        self.background = pygame.transform.scale(bc, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        self.game_over = pygame.image.load(get_resource_path('resources/image/gameover.png'))
        # 加载启动界面背景
        start_bc = pygame.image.load(get_resource_path('resources/image/plane-code.png'))
        self.start_background = pygame.transform.scale(start_bc, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()

    def show_start_screen(self):
        """
        显示启动界面
        """
        start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 200, 200, 50, "开始游戏")
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.screen.fill(0)
            self.screen.blit(self.start_background, (0, 0))
            start_button.draw(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                if start_button.handle_event(event):
                    running = False
                    
            pygame.display.update()
            clock.tick(60)
    
    def run(self):
        """
        游戏主循环
        """
        # 显示启动界面
        self.show_start_screen()

        if not self.config.get("serial_config", None) \
            or not self.config.get("serial_config").get("port", None) \
            or not self.config.get("serial_config").get("baudrate", None):
            self.config_edit()
        else:  
            self.startGame()

        while True:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.screen.get_rect().centerx - 70 <= event.pos[0] \
                            and event.pos[0] <= self.screen.get_rect().centerx + 50 \
                            and self.screen.get_rect().centery + 100 <= event.pos[1] \
                            and self.screen.get_rect().centery + 140 >= event.pos[1]:

                        self.startGame()
                    if self.screen.get_rect().centerx - 70 <= event.pos[0] \
                            and event.pos[0] <= self.screen.get_rect().centerx + 50 \
                            and self.screen.get_rect().centery + 160 <= event.pos[1] \
                            and self.screen.get_rect().centery + 200 >= event.pos[1]:
                        self.game_ranking()

                    if self.screen.get_rect().centerx - 70 <= event.pos[0] \
                            and event.pos[0] <= self.screen.get_rect().centerx + 50 \
                            and self.screen.get_rect().centery + 235 <= event.pos[1] \
                            and self.screen.get_rect().centery + 275 >= event.pos[1]:

                        self.config_edit()

            pygame.display.update()

    def exit_game(self):
        pygame.quit()
        exit()

    def startGame(self):
        try:
            if not self.serial_thread or not self.serial_thread.is_alive() or not self.serial_thread.running:
                self.serial_thread = SerialDevice(self.serial_data_queue, self.config["serial_config"]["port"], self.config["serial_config"]["baudrate"])
                self.serial_thread.start()
            else:
                self.serial_thread.close()
                self.serial_thread.join()
                self.serial_thread = SerialDevice(self.serial_data_queue, self.config["serial_config"]["port"], self.config["serial_config"]["baudrate"])
                self.serial_thread.start()
            
        except Exception as e:
            print(f"串口通信线程创建失败: {e}")
            self.serial_thread = None
        
        player_pos = [200, 520]
        player = Player(player_pos, self.plane_controller)
        enemies1 = pygame.sprite.Group()
        enemies_down = pygame.sprite.Group()
        shoot_frequency = 0
        enemy_frequency = 0
        player_down_index = 16
        score = 0
        clock = pygame.time.Clock()
        running = True
        
        self.serial_data_queue.queue.clear()
        while running:
            self.screen.fill(0)
            self.screen.blit(self.background, (0, 0))

            if self.serial_thread and self.serial_thread.is_alive() and self.serial_thread.running:
                text = get_sys_font(20).render(f"{self.config['serial_config']['port']} OK", True, (0, 255, 0))
            else:
                text = get_sys_font(20).render(f"{self.config['serial_config']['port']} ERR", True, (255, 0, 0))
            text_rect = text.get_rect()
            text_rect.centerx = self.screen.get_rect().centerx
            text_rect.centery = 20
            self.screen.blit(text, text_rect)

            serial_data_list = []
            while not self.serial_data_queue.empty():
                serial_data_list.append(self.serial_data_queue.get())
            player.deal_serial_data(serial_data_list)

            # 控制游戏最大帧率为 60
            clock.tick(60)
            # 生成子弹，需要控制发射频率
            # 首先判断玩家飞机没有被击中


            for bullet in player.bullets:
                # 以固定速度移动子弹
                bullet.move()
                # 移动出屏幕后删除子弹
                if bullet.rect.bottom < 0:
                    player.bullets.remove(bullet)
            # 显示子弹
            player.bullets.draw(self.screen)
            # 生成敌机，需要控制生成频率
            if enemy_frequency % 50 == 0:
                enemy1 = Enemy()
                enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1.get_width()), 0]
                enemy1.set_pos(enemy1_pos)
                enemies1.add(enemy1)
            enemy_frequency += 1
            if enemy_frequency >= 100:
                enemy_frequency = 0
            for enemy in enemies1:
                # 移动敌机
                enemy.move()
                if pygame.sprite.collide_mask(enemy, player):
                    # enemies_down.add(enemy)
                    enemies1.remove(enemy)
                    player.is_hit = True
                    break
                # 移动出屏幕后删除飞机
                if enemy.rect.top > SCREEN_HEIGHT:
                    enemies1.remove(enemy)
            # 敌机被子弹击中效果处理
            # 将被击中的敌机对象添加到击毁敌机 Group 中，用来渲染击毁动画
            # 方法groupcollide()是检测两个精灵组中精灵们的矩形冲突
            enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1)
            # 遍历key值 返回的碰撞敌机对象
            for enemy_down in enemies1_down:
                # 点击销毁的敌机到列表
                enemies_down.add(enemy_down)
            # 绘制玩家飞机
            if not player.is_hit:
                self.screen.blit(player.image[player.img_index], player.rect)
                # 更换图片索引使飞机有动画效果
                player.img_index = shoot_frequency // 8
            else:
                # 玩家飞机被击中后的效果处理
                player.img_index = player_down_index // 8
                self.screen.blit(player.image[player.img_index], player.rect)
                player_down_index += 1
                if player_down_index > 47:
                    # 击中效果处理完成后游戏结束
                    running = False
            # 敌机被子弹击中效果显示
            for enemy_down in enemies_down:
                if enemy_down.down_index == 0:
                    pass
                if enemy_down.down_index > 7:
                    enemies_down.remove(enemy_down)
                    score += 100
                    continue
                #显示碰撞图片
                self.screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
                enemy_down.down_index += 1
            # 显示精灵
            enemies1.draw(self.screen)
            # 绘制当前得分
            score_font = get_sys_font(36)
            score_text = score_font.render(str(score), True, (255, 255, 255))
            text_rect = score_text.get_rect()
            text_rect.topleft = [10, 10]
            self.screen.blit(score_text, text_rect)
            # 更新屏幕
            pygame.display.update()
            # 处理游戏退出
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
            # 获取键盘事件（上下左右按键）
            key_pressed = pygame.key.get_pressed()
            self.plane_controller.deal_key_event(key_pressed, player)

        # 关闭串口
        self.serial_thread.close()
        # 绘制游戏结束背景
        self.screen.blit(self.game_over, (0, 0))
        # 游戏 Game Over 后显示最终得分
        font = pygame.font.Font(None, 48)
        text = font.render('Score: ' + str(score), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = self.screen.get_rect().centery + 24
        self.screen.blit(text, text_rect)
        # 获取系统字体
        xtfont = get_sys_font(30)
        # 重新开始按钮
        textstart = xtfont.render('重新开始 ', True, (255, 255, 255))
        text_rect = textstart.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = self.screen.get_rect().centery + 120
        self.screen.blit(textstart, text_rect)
        # 排行榜按钮
        textstart = xtfont.render('排行榜 ', True, (255, 255, 255))
        text_rect = textstart.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = self.screen.get_rect().centery + 180
        self.screen.blit(textstart, text_rect)
        textstart = xtfont.render('串口配置 ', True, (255, 255, 255))
        text_rect = textstart.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = self.screen.get_rect().centery + 240
        self.screen.blit(textstart, text_rect)
        self.update_score(score)

    def get_score_list(self) -> list[dict]:
        return self.config.get("game_scroes", [])

    def update_score(self, score) -> list[dict]:
        score_list = self.config.get("game_scroes", [])
        score_list.append({"score": score, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        score_list.sort(key=lambda x: x["score"], reverse=True)
        score_list = score_list[:10]
        self.config["game_scroes"] = score_list
        save_config(self.config)
        return score_list

    def game_ranking(self) -> None:
        # 创建排行榜窗口
        self.screen2 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 绘制背景
        self.screen2.fill(0)
        self.screen2.blit(self.background, (0, 0))
        xtfont = get_sys_font(30)

        textstart = xtfont.render('排行榜', True, (255, 0, 0))
        text_rect = textstart.get_rect()
        text_rect.centerx = self.screen2.get_rect().centerx
        text_rect.centery = 40
        self.screen2.blit(textstart, text_rect)
        # 重新开始按钮
        textstart = xtfont.render('开始游戏', True, (255, 0, 0))
        text_rect = textstart.get_rect()
        text_rect.centerx = self.screen2.get_rect().centerx
        text_rect.centery = self.screen2.get_rect().centery + 120
        self.screen2.blit(textstart, text_rect)

        arrayscore = self.get_score_list()

        
        tmp_x = 0

        for i in range(0, len(arrayscore)):
            # 游戏 Game Over 后显示最终得分
            font = pygame.font.Font(None, 48)
            # 绘制排名, 字符串格式：排名 + 分数
            txt_str = f"{i+1:02d}    {arrayscore[i]['score']}"
            text = font.render(txt_str, True, (255, 0, 0))
            text_rect = text.get_rect()
            text_rect.centerx = self.screen2.get_rect().centerx
            if tmp_x == 0:
                tmp_x = text_rect.left
            else:
                text_rect.left = tmp_x
            text_rect.centery = 80 + 30*i
            # 绘制分数内容
            self.screen2.blit(text, text_rect)




    def config_edit(self):
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('串口配置')
        port_box = InputBox(150, 110, 200, 40, 
                        text=self.config.get('serial_config', {}).get('port', ''))
        baudrate_box = InputBox(150, 210, 200, 40, 
                            text=str(self.config.get('serial_config', {}).get('baudrate', '')))
        save_button = Button(150, 310, 200, 40, "OK")
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            screen.fill((30, 30, 30))
            
            font = get_sys_font(32)
            title = font.render('串口配置', True, (255, 255, 255))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
            
            label_font = get_sys_font(24)
            port_label = label_font.render('串口:', True, (255, 255, 255))
            baudrate_label = label_font.render('波特率:', True, (255, 255, 255))
            screen.blit(port_label, (50, 110))
            screen.blit(baudrate_label, (50, 210))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.exit_game()
                    
                port_box.handle_event(event)
                baudrate_box.handle_event(event)
                
                if save_button.handle_event(event):
                    try:
                        baudrate = int(baudrate_box.text)
                        self.config['serial_config'] = {
                            'port': port_box.text,
                            'baudrate': baudrate
                        }
                        save_config(self.config)
                        running = False
                    except ValueError:
                        print("波特率必须是数字")
            
            port_box.draw(screen)
            baudrate_box.draw(screen)
            save_button.draw(screen)
            
            pygame.display.flip()
            clock.tick(60)
        self.game_ranking()



def get_sys_font(size):
    try:
        current_os = platform.system()
        if current_os == 'Windows':
            font_paths = [
                "C:\\Windows\\Fonts\\msyh.ttc",
                "C:\\Windows\\Fonts\\simsun.ttc",
            ]
        elif current_os == 'Darwin':
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]
        else:
            font_paths = [
                "/usr/share/fonts/wenquanyi/wqy-microhei.ttc",
                "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            ]

        for font_path in font_paths:
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
        return pygame.font.SysFont('arial', size)
    except:
        return pygame.font.Font(None, size)

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
