from time import time as timer
from random import randint

from pygame import *


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, speed, size_x, size_y):
        super().__init__()
        self.image = transform.scale(image.load(img), (size_x, size_y))    
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if (keys[K_LEFT] or keys[K_a]) and self.rect.x > 0:
            self.rect.x -= self.speed
        if (keys[K_RIGHT] or keys[K_d]) and self.rect.right < win_width:
            self.rect.x += self.speed
    
    def fire(self, target_x, target_y):
        fire_sound.play()
        bullets.add(
            Bullet(
                img_bullet,
                self.rect.centerx - (15 // 2), self.rect.top,
                30, # speed
                15, 15,
                target_x, target_y
            )
        )
        
        
class Enemy(GameSprite):
    def __init__(self, img, x, y, speed, size_x, size_y, is_lost_inc=True):
        super().__init__(img, x, y, speed, size_x, size_y)
        self.is_lost_inc = is_lost_inc
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = randint(0, win_width - 80)
            self.speed = randint(1, 5) # TODO
            
            if self.is_lost_inc:
                global lost
                lost += 1
            
class Bullet(GameSprite):
    def __init__(self, img, x, y, speed, size_x, size_y, 
                 target_x, target_y):
        super().__init__(img, x, y, speed, size_x, size_y)
        
        # Рассчитываем вектор скорости от текущей позиции до цели
        dx = target_x - x
        dy = target_y - y
        
        # Нормализуем вектор скорости
        distance = (dx**2 + dy**2)**0.5
        if distance == 0: distance = 1  # предотвращаем деление на ноль
        self.speed_x = speed * (dx / distance)
        self.speed_y = speed * (dy / distance)
        
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Проверяем, вышла ли пуля за пределы экрана
        if self.rect.y < -10 or self.rect.y > win_height or self.rect.x < -10 or self.rect.x > win_width:
            self.kill()

lost = 0
score = 0

max_lost = 3
goal_score = 10

img_background = "galaxy.jpg"
img_rocket = "rocket.png"
music_background = "space.ogg"
img_enemy = "ufo.png"
img_asteroid = "asteroid.png"
img_bullet = "bullet.png"
music_fire = "fire.ogg"

rocket_size_x = 80
rocket_size_y = 100
rocket_speed = 10

mixer.init()
mixer.music.load(music_background)
mixer.music.play()

fire_sound = mixer.Sound(music_fire)

font.init()
label_font = font.Font(None, 36)

win_width = 700
win_height = 500

window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")
background = transform.scale(
    image.load(img_background), (win_width, win_height)
)

ship = Player(
    img_rocket, 
    (win_width // 2) - (rocket_size_x // 2), 
    win_height - rocket_size_y,
    rocket_speed,
    rocket_size_x, rocket_size_y
)

monsters = sprite.Group()
for _ in range(5):
    monsters.add(
        Enemy(img_enemy, 
              randint(0, win_width - 80), -40,
              randint(1, 5),
              80, 50)
    )

asteroids = sprite.Group()
for _ in range(3):
    asteroids.add(
        Enemy(img_asteroid, 
              randint(0, win_width - 80), -40,
              randint(3, 8),
              40, 25, False)
    )

bullets = sprite.Group()

finish = False
run = True

reload_time = False
num_shot = 0
start_time_reload = None

while run:
    time.delay(50)
    
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            if not reload_time and num_shot < 5:
                ship.fire(*e.pos)
                num_shot += 1
            if num_shot >= 5 and not reload_time:
                reload_time = True
                start_time_reload = timer()
        if e.type == KEYDOWN and e.key == K_r and finish:
            for m in monsters:
                m.kill()
            for b in bullets:
                b.kill()
            for a in asteroids:
                a.kill()
            
            lost = 0
            score = 0
            num_shot = 0
            reload_time = False
            
            for _ in range(5):
                monsters.add(
                    Enemy(img_enemy, 
                        randint(0, win_width - 80), -40,
                        randint(1, 5),
                        80, 50)
                )
            
            for _ in range(3):
                asteroids.add(
                    Enemy(img_asteroid, 
                        randint(0, win_width - 80), -40,
                        randint(3, 8),
                        40, 25, False)
                )
                
            ship.rect.x = (win_width // 2) - (rocket_size_x // 2)
            ship.rect.y = win_height - rocket_size_y
            
            finish = False
            
    if not finish:
        window.blit(background, (0, 0))
        
        monsters.update()
        monsters.draw(window)
        
        bullets.update()
        bullets.draw(window)
        
        asteroids.update()
        asteroids.draw(window)
        
        ship.update()
        ship.reset()
        
        window.blit(
            label_font.render(
                f"Счет: {score}", True, (255, 255, 255)
            ), (10, 30)
        )
        
        window.blit(
            label_font.render(
                f"Пропушено: {lost}", True, (255, 255, 255)
            ), (10, 50)
        )
        
        if reload_time:
            left_time_reload = max(0, round(2 - (timer() - start_time_reload), 2))
            window.blit(
                label_font.render(
                    f"Wait, reload... {left_time_reload}с.",
                    True, 
                    (255, 255, 255)
                ), (260, 460)
            )
            
            if timer() - start_time_reload >= 2:
                num_shot = 0
                reload_time = False
        
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for _ in collides:
            score += 1
            monsters.add(
                Enemy(img_enemy, 
                    randint(0, win_width - 80), -40,
                    randint(1, 5),
                    80, 50)
            )
            
        sprite.groupcollide(asteroids, bullets, False, True)
        
        if score > goal_score:
            finish = True
            window.blit(
                font.Font(None, 80).render(
                    "YOU WIN!", True, (0, 255, 0)
                    ),
                (200, 200)
            )
            window.blit(
                font.Font(None, 30).render(
                    "Нажмите 'R' для перезапуска игры", True, (255, 255, 255)
                    ),
                (165, 270)
            )
            
        if (lost > max_lost 
            or sprite.spritecollide(ship, monsters, False) 
            or sprite.spritecollide(ship, asteroids, False)):
            finish = True
            window.blit(
                font.Font(None, 70).render("YOU LOSE!", True, (255, 0, 0)),
                (200, 200)
            )
            window.blit(
                font.Font(None, 30).render(
                    "Нажмите 'R' для перезапуска игры", True, (255, 255, 255)
                    ),
                (165, 270)
            )
        
        display.update()