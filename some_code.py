# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
import pygame
import random
import os
import math
from os import path
import time

WIDTH = 800
HEIGHT = 600
FPS = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (225,225,0)

game_folder=os.path.dirname(__file__)
img_dir=path.join(path.dirname(__file__),"img")
snd_dir=path.join(path.dirname(__file__),"snd")

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pygame_game")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, GREEN)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_shield(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(ship_img,(70,70))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius=35
        #pygame.draw.circle(image, RED,self.rect.center, self.radius)
        self.rect.centerx=WIDTH
        self.rect.bottom=HEIGHT-10
        self.speedx=0
        self.sheild=100
        self.shoot_del=250
        self.last_shoot=pygame.time.get_ticks()
        self.lives=3
        self.hidden=False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -4
        if keystate[pygame.K_RIGHT]:
            self.speedx = 4
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_del:
            self.last_shoot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image=self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius=int(self.rect.width*.9/2)
        #pygame.draw.circle(self.image, RED,self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot=0
        self.rot_speed=random.randrange(-8,8)
        self.last_update=pygame.time.get_ticks()
    def rotate(self):
        now=pygame.time.get_ticks()
        if now-self.last_update>50:
            self.last_update=now
            self.rot=(self.rot+self.rot_speed)%360
            new_image=pygame.transform.rotate(self.image_orig,self.rot)
            old_center=self.rect.center
            self.image=new_image
            self.rect=self.image.get_rect()
            self.rect.center=old_center
        
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img,(13,34))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()
class Pow(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center=center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


background=pygame.image.load(path.join(img_dir,"starfield.png")).convert()
background_rect=background.get_rect()
ship_img=pygame.image.load(path.join(img_dir,"playerShip1_orange.png")).convert()
ship_mini_img = pygame.transform.scale(ship_img, (25, 19))
ship_mini_img.set_colorkey(BLACK)
laser_img=pygame.image.load(path.join(img_dir,"laserRed16.png")).convert()
meteor_img=pygame.image.load(path.join(img_dir,"meteorBrown_med1.png")).convert()
meteor_images=[]
meteor_list=['meteorBrown_med1.png','meteorBrown_med3.png','meteorBrown_small1.png','meteorBrown_small2.png','meteorBrown_tiny1.png']
for i in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, i)).convert())
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()
expl_sounds=[]
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
shoot_sound=pygame.mixer.Sound(path.join(snd_dir,"pew.wav"))
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
pygame.mixer.music.load(path.join(snd_dir,"tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.01)

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
ship=Ship()
all_sprites.add(ship)
for i in range(20):
    m=Mob()
    mobs.add(m)
    all_sprites.add(m)
score=0
pygame.mixer.music.play(loops=-1)
    
running=True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
    all_sprites.update()
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if random.random() > 0.75:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
    if hits:
        score=score+5
    if len(mobs)==0:
        draw_text(screen,"You Win",20,400,300)
        pygame.display.update()
        time.sleep(5)
        running=False
    hits = pygame.sprite.spritecollide(ship, mobs, True,pygame.sprite.collide_circle)
    for hit in hits:
        ship.sheild-=hit.radius*2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if ship.sheild<=0:
            player_die_sound.play()
            death_explosion = Explosion(ship.rect.center, 'player')
            all_sprites.add(death_explosion)
            ship.hide()
            ship.lives-=1
            if ship.lives !=0:
                ship.sheild=100

    if ship.lives==0 and not death_explosion.alive():
        draw_text(screen,"You Lose",20,450,300)
        running = False
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_shield(screen,5,5,ship.sheild)
    draw_lives(screen,WIDTH-100,5,ship.lives,ship_mini_img)
    pygame.display.flip()       
draw_text(screen,"Your score was",20,450,300)
pygame.display.update()
draw_text(screen,str(score),20,550,300)
pygame.display.update()
time.sleep(5)
pygame.quit()

