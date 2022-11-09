import sys
import random
#https://biquyetxaynha.com/huong-dan-dung-python-event-python
import pygame
import os
from pygame.locals import *

#Dòng này cần phải có để sử dụng các hàm của pygame, chỉ cần biết khi dùng pygame thì nhớ thêm dòng này vào.
pygame.init()

''' IMAGES '''
player_ship = 'player_ship.png'
enemy_ship = 'enemy_ship.png'
enemy_ship2 = 'enemy_ship2.png'
enemy_ship3 = 'enemy_ship3.png'
enemy_ship4 = 'enemy_ship4.png'
ufo_ship = 'ufo_ship.png'

player_bullet = 'player_bullet.png'
enemy_bullet = 'enemy_bullet.png'
enemy_bullet2 = 'enemy_bullet2.png'
enemy_bullet3 = 'enemy_bullet3.png'
enemy_bullet4 = 'enemy_bullet4.png'
ufo_bullet = 'enemy_bullet.png'
heart_lives = 'heart_lives.png'

screen = pygame.display.set_mode((0, 0), FULLSCREEN)
pygame.display.set_caption('Space Shooter Group 18')
s_width, s_height = screen.get_size() #800, 600

#backgrounds image
Start_BG = pygame.transform.scale(pygame.image.load(os.path.join("start_bg.png")), (s_width, s_height))
Game_BG = pygame.transform.scale(pygame.image.load(os.path.join("game_bg.png")), (s_width, s_height))
Game_Over_BG = pygame.transform.scale(pygame.image.load(os.path.join("game_over_bg.png")), (s_width, s_height))


'''SOUND'''
player_bullet_sound = pygame.mixer.Sound('player_bullet.wav')
explosion_sound = pygame.mixer.Sound('explosion.wav') 
go_game_sound = pygame.mixer.Sound('go_game.wav') 
game_over_sound = pygame.mixer.Sound('game_over.wav') 
start_screen_music = pygame.mixer.Sound('start_screen.mp3')
bg_music = pygame.mixer.music.load('bg_music.mp3')
over_game_music = pygame.mixer.Sound('over_game.mp3')
pygame.mixer.init()

clock = pygame.time.Clock()
FPS = 80

#pygame.sprite.Group(): Một lớp vùng chứa để giữ và quản lý nhiều đối tượng Sprite (na ná 1 list chứa các đối tượng giống nhau như list <Integer> :v kiểu vậy)
#Những đối tượng bằng hình vẽ được gọi là sprites (ma quỉ) trên màn hình vì chúng di chuyển, trôi nổi trên nền màn hình
background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerBullet_group = pygame.sprite.Group()
enemyBullet_group = pygame.sprite.Group()
ufoBullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


#chứa TẤT CẢ các sprite của game, chỉ cần sprite_group.update(), thì tất cả các sprite của game( ufo, player, enemy, ufoBullet, enemyBullet, playerBullet, background_image) đều gọi ra hàm update(), hàm update() của từng sprite để tăng tọa độ (rect) và dùng nó để di chuyển
sprite_group = pygame.sprite.Group() 

BulletEnemyReceived = {} #cái dict này để đếm số đạn từng kẻ địch đã bị bắn
#với key là các sprite enemy, value là số đạn người chơi đã bắn vào tàu đó (cài đặt bị
# bắn 2 lần thì tàu cút nhé :v)
BulletUfoReceived = {} #tương tự cái trên thì cái này để đếm số đạn mà ufo bị bắn 
#(cài đặt tầm 20 lần bắn ufo)

pygame.mouse.set_visible(False)

#pygame.sprite.Sprite được gọi là phần nới rộng (extending) thêm của Pygame. Khi bạn tạo một class 'cho Sprite' bạn cần gọi pygame này:
#pygame.sprite.Sprite, trong đó chứa tất cả những gì cần thiết cho đồ hoạ sprite (sprite graphics).   
class Background(pygame.sprite.Sprite): #kế thừa từ pygame.sprite.Sprite
    def __init__(self, width, height): #width, height của khối surface

        #update: chắc là chạy cái này đế lấy các thuộc tính làm việc của thằng cha là pygame.sprite.Sprite :v
        super().__init__() #chưa hiểu cái này để làm gì, biết là super để dùng được method của thằng cha rùi, nma dùng với mục đích gì, tạo sao lại phải gọi init của hàm cha, 

        #Surface trong pygame là 1 nơi dùng để vẽ lên, ở đây tạo 1  surface có width, height = width, height
        #nó đang tạo ra các hình vuông có chiều dài width, chiều cao height để làm background
        self.image = pygame.Surface([width, height])
        self.image.fill('white') #tạo màu của surface

        #src: https://helpex.vn/question/cach-tao-be-mat-co-nen-trong-suot-trong-pygame-60ce85eff137b0e523f943cc
        self.image.set_colorkey('black') #tạo màu trong suốt của surface
        self.rect = self.image.get_rect() #lấy ra vị trí của khối surface đó để check chạm biên


    #Cập nhật những sprites cho một khung hình (frame) là thay đổi vị trí của mỗi sprite tuỳ theo vận tốc của nó và kiểm soát xem nó có đụng vào thành của màn hình chưa.
    
    def update(self):
        #x,y ở đây là đi từ rect, là tọa độ của khối surface, tăng lên 1 để di chuyển các khối surface đó
        self.rect.x += 1 
        self.rect.y += 1
        if self.rect.y > s_height: #nếu nó chạm biên thì set lại x, y của khối đó
            self.rect.x = random.randrange(-40, s_width)
            self.rect.y = random.randrange(-10, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.image.set_colorkey("black")

        self.alive = True
        self.count_to_live_again = 0 #đếm thời gian hồi sinh
        self.activate_bullet = True #để khi chết thì player không bắn đc đạn
        self.alpha_duration = 0

    def update(self):
        if self.alive:
            #nhap nhay khi hoi sinh
            self.image.set_alpha(130)
            self.alpha_duration += 1
            if self.alpha_duration > 100:
                    self.image.set_alpha(255)

            mouse = pygame.mouse.get_pos() #lấy ra vị trí con trỏ chuột
            self.rect.x = mouse[0] - 28 #trừ 28 vì mình lấy x ở tại con trỏ chuột nên phi thuyền sẽ nằm ở vị trí (0,0) so với con trỏ chuột, trừ tọa độ phi thuyển đi tầm 28 để con trỏ chuột đặt ở giữa ohi thuyền (CÓ THỂ XÓA -28 ĐI RỒI CHẠY ĐÊ HIỂU RÕ HƠN)
            self.rect.y = mouse[1] - 36
        else:
            self.alpha_duration = 0
            expl_x = self.rect.x + 52
            expl_y = self.rect.y + 62
            explosion = Explosion(expl_x,expl_y)
            explosion_group.add(explosion)
            sprite_group.add(explosion_group)

            pygame.time.delay(12) #Khi player chết thì slow game lại 16ms
            self.rect.y = s_height + 200 #+200 để làm player_ship biến mất khỏi screen 1 lúc
            self.count_to_live_again += 1
            if self.count_to_live_again > 80:
                self.alive = True
                self.activate_bullet = True
                self.count_to_live_again = 0

    def shoot(self):
        if self.activate_bullet:
            pygame.mixer.Sound.play(player_bullet_sound)
            bullet = PlayerBullet(player_bullet)
            #vị trí viên đạn bằng với vị trí của phi thuyền, +22 chỉ để căn chỉnh lại cho viên đạn ra giữa phi thuyền mang tính thẩm mĩ
            bullet.rect.x = self.rect.x + 42
            bullet.rect.y = self.rect.y - 42
            playerBullet_group.add(bullet)
            sprite_group.add(bullet)

    def dead(self):
        self.alive = False
        self.activate_bullet = False

class Enemy(Player): #kế thừa từ Player

    def __init__(self, img, enemy_bullet):
        super().__init__(img) #gọi đến __init__ của class Player (hình ảnh địch)
        self.enemy_bullet = enemy_bullet #hình ảnh đạn địch
        self.enemyBullet = EnemyBullet(self.enemy_bullet) #class chứa đạn địch, mỗi thằng enemy đều gắn liền với đạn của nó, khai 
        #khi nó chết thì phải kill() thằng đạn của nó đi cùng
        self.image = pygame.transform.scale(self.image, (160, 160))

        self.rect.x = random.randrange(160, s_width - 200)
        self.rect.y = random.randrange(-500, -50)
        #Hàm blit dùng để vẽ 1 surface lên 1 surface khác.
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(160, s_width - 200)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()

    def shoot(self):
        if self.rect.y in (0, 180, 300):
            self.enemyBullet = EnemyBullet(self.enemy_bullet)
            self.enemyBullet.rect.x = self.rect.x + 52 #cộng 16 chủ yếu để căn chỉnh lại hình ảnh so để nó nằm đẹp hơn :v
            self.enemyBullet.rect.y = self.rect.y + 104
            enemyBullet_group.add(self.enemyBullet)
            sprite_group.add(self.enemyBullet)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.image = pygame.transform.scale(self.image, (15, 71))

        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')

    def update(self):
        self.rect.y -= 5
        if self.rect.y < 0: #nếu chạm top thì kill viên đạn đó đi
            self.kill() 

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.image.set_colorkey('white')

    def update(self):
        self.rect.y += 3
        if self.rect.y > s_height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'exp{i}.png')
            img.set_colorkey('black')
            img = pygame.transform.scale(img, (120, 120))
            self.img_list.append(img)
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.count_delay = 0 
 
    def update(self):
        self.count_delay += 1

        if self.index >= len(self.img_list) - 1:
            if self.count_delay >= 6: self.kill()

        elif self.count_delay >= 6:
            self.count_delay = 0
            self.index += 1
            self.image = self.img_list[self.index]

class Game:
    #'self' like 'this' keyword in java/js,...
    def __init__(self): #hàm khởi tạo
        self.lives = 5
        self.score = 0

        #de Khi game over xong said "GAME OVER" xong 1 luc moi phat nhac nen game over
        self.count_over_sound_delay = 0 
        self.start_screen()

    def start_screen(self):
        pygame.mixer.Sound.play(start_screen_music)
        screen.blit(Start_BG, (0, 0))
        while True:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: #Ấn nút Esc
                        pygame.quit()
                        sys.exit()
                    else: self.run_game()

    def game_over_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(game_over_sound)
        screen.blit(Game_Over_BG, (0, 0))
        while True:
            font = pygame.font.SysFont('Road Rage', 82)
            text = font.render(str(self.score), True, 'white')
            screen.blit(text, (900, 457))
            pygame.display.update()

            self.count_over_sound_delay += 1
            #sau khi noi "GAME OVER" thi moi play over_game_music
            if self.count_over_sound_delay > 1800: 
                pygame.mixer.Sound.play(over_game_music)
                self.count_over_sound_delay = 0

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_t: #Ấn phím t để tiếp tục
                        self.start_new_game()
                    if event.key == K_ESCAPE or event.key == K_x: #Ấn nút Esc
                        pygame.quit()
                        sys.exit()
    
    def start_new_game(self):
        self.lives = 5
        self.score = 0

        #clear all sprite in game
        sprite_group.empty()
        self.run_game()

    def create_background(self): #tạo background với x, y của khối surface
        screen.blit(Game_BG, (0, 0))
        for i in range(20): #tạo 20 khối surface trên màn hình( tạo 1 lần rồi di chuyển chúng là xong )
            x = random.randint(1,5)
            background_image = Background(x, x)
            background_image.rect.x = random.randrange(0, s_width)
            background_image.rect.y = random.randrange(0, s_height)

            #2 thằng này là 1 group chứa các sprite (background_image) - xem lại dòng 19, 20
            background_group.add(background_image)
            sprite_group.add(background_image)
    
    def create_player(self):
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player)

    def create_enemy(self):
        for i in range(2):
            self.enemy = Enemy(enemy_ship, enemy_bullet)
            self.enemy2 = Enemy(enemy_ship2, enemy_bullet2)
            self.enemy3 = Enemy(enemy_ship3, enemy_bullet3)
            self.enemy4 = Enemy(enemy_ship4, enemy_bullet4)

            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)
            
            enemy_group.add(self.enemy2)
            sprite_group.add(self.enemy2)

            enemy_group.add(self.enemy3)
            sprite_group.add(self.enemy3)
            
            enemy_group.add(self.enemy4)
            sprite_group.add(self.enemy4)

    #SRC: https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.groupcollide
    #Đầu ra của groupcollide là một dictionary với key là một sprite từ nhóm đầu tiên 
    #và value là danh sách tất cả các sprite từ nhóm thứ hai mà key sprite đang va chạm (nó sử dụng rect để tính sự va chạm)
    def playerbullet_hits_enemy(self):
        hits = pygame.sprite.groupcollide(enemy_group, playerBullet_group, False, True)
        for i in hits: #i là các sprite của enemy gruop
            # print(i, hits[i])
            if not(i in BulletEnemyReceived): BulletEnemyReceived[i] = 1
            else: BulletEnemyReceived[i] += 1
            
            #nếu tàu địch nào đã nhận đủ 2 viên, thì nó biến mất vì đã được reset rect về sau cánh gà :v
            if (BulletEnemyReceived[i] == 2):
                pygame.mixer.Sound.play(explosion_sound)
                self.score += 10
                expl_x = i.rect.x + 85
                expl_y = i.rect.y + 110
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)

                #2 dòng x, y dưới đây là reset rect về sau cánh gà nè :v
                #160 tránh TH nó sát mép trái
                #-200 tránh TH nó vượt qua mép phải
                i.enemyBullet.kill() #Nếu kẻ địch chết thì xóa luôn đạn của địch
                i.rect.x = random.randrange(160, s_width - 200)
                i.rect.y = random.randrange(-300, -100)
                BulletEnemyReceived[i] = 0
            

    def enemyBullet_hits_player(self):
        if self.player.image.get_alpha() == 255:
            #spritecollide: Simple test if a sprite intersects anything in a group.
            hits = pygame.sprite.spritecollide(self.player, enemyBullet_group, True)
            if hits: #nếu có sự va chạm nào thì:
                pygame.mixer.Sound.play(explosion_sound)
                self.lives -= 1
                self.player.dead()
                if (self.lives < 1):
                    self.game_over_screen()

    def player_enemy_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
            if hits:
                pygame.mixer.Sound.play(explosion_sound)
                for i in hits:
                    i.rect.x = random.randrange(0, s_width)
                    i.rect.y = random.randrange(-3000, -100)
                    self.lives -= 1
                    self.player.dead()
                    if self.lives < 1:
                        self.game_over_screen()

    def create_heart_lives(self):
        self.live_img = pygame.image.load(heart_lives)
        self.live_img = pygame.transform.scale(self.live_img, (30, 30))
        n = 0
        for i in range(self.lives): #lives là số lượng mạng còn lại
            screen.blit(self.live_img, (30 + n, s_height - 50))
            n += 50

    def create_score(self):
        score = self.score
        font = pygame.font.SysFont('Road Rage', 42)
        text = font.render("Score: " + str(score), True, (204, 204, 0))
        screen.blit(text, (30, s_height - 90))

    def run_update(self):
        ##draws all sprites in the group
        sprite_group.draw(screen) #vẽ cái vùng chứa các sprite( các khối surface ) lên màn hình

        #Calls the update function on all sprites in group
        sprite_group.update() 
        #chứa TẤT CẢ các sprite của game, chỉ cần sprite_group.update(), thì tất cả các sprite của game( ufo, player, enemy, ufoBullet, enemyBullet, playerBullet, background_image) đều gọi ra hàm update(), hàm update() để tăng tọa độ từng sprite và dùng nó để di chuyển

    def run_game(self):
        pygame.mixer.Sound.stop(start_screen_music)
        pygame.mixer.Sound.stop(over_game_music)
        pygame.mixer.Sound.play(go_game_sound)
        pygame.mixer.music.play()
        self.create_background() #tạo ra 20 khối surface trên màn hình
        self.create_player()
        self.create_enemy()
        while True:
            screen.blit(Game_BG, (0, 0))
            # screen.fill(Game_BG, (0, 0)) của background, để trong while True vì không thể xóa thằng surface trước khi += 1 tọa độ, nên mỗi lần += 1 thì update lại màu background, NÊN THỬ ĐỂ BÊN NGOÀI WHITE TRUE ĐỂ THẤY RÕ NÓ CHẠY NHƯ THẾ NÀO
            self.playerbullet_hits_enemy()
            self.enemyBullet_hits_player()
            self.player_enemy_crash()
            self.create_heart_lives()
            self.create_score()

            self.run_update() #di chuyển 20 khối surface trên màn hình
            for event in pygame.event.get():
                if event.type == QUIT: #Click vào nút X
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_DOWN: #Ấn nút Esc
                        self.player.shoot()
                    if event.key == K_ESCAPE: #Ấn nút Esc
                        pygame.quit()
                        sys.exit()
            #update: function được gọi trong function run của game, đảm nhiệm việc cập nhật trạng thái các nhân vật trong game qua từng khung hình
            pygame.display.update()
            clock.tick(FPS)

def main():
    game = Game()

main()
# if __name__ == '__main__':
#     main()
                