import pygame
from pygame import mixer
import random

pygame.init()

WIDTH, HEIGHT = 700, 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космо шутер")
clock = pygame.time.Clock()
FPS = 60

background = pygame.image.load('space_background.jpg')
mixer.music.load('space.ogg')
mixer.music.play(-1)

fire_sound = mixer.Sound('fire.ogg')

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, speed=0):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image_path, x, y, speed=5):
        super().__init__(image_path, x, y, speed)

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.x < 0:
                self.rect.x = 0
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.x > WIDTH - self.rect.width:
                self.rect.x = WIDTH - self.rect.width

class Enemy(GameSprite):
    def __init__(self, image_path, x, y, speed=2):
        super().__init__(image_path, x, y, speed)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-150, -40)

original_ufo_image = pygame.image.load('ufo.png')
ufo_width = original_ufo_image.get_width()
ufo_height = original_ufo_image.get_height()

scaled_width = ufo_width // 9
scaled_height = ufo_height // 9
scaled_ufo_image = pygame.transform.scale(original_ufo_image, (scaled_width, scaled_height))

enemy_count = 5
enemies = pygame.sprite.Group()

interval_x = (WIDTH - scaled_width * enemy_count) // (enemy_count + 1)

for i in range(enemy_count):
    enemy_x = interval_x + i * (scaled_width + interval_x)
    enemy_y = random.randint(-150, -40)
    enemy = Enemy('ufo.png', enemy_x, enemy_y, speed=2)
    enemy.image = scaled_ufo_image
    enemy.rect = enemy.image.get_rect()
    enemy.rect.x = enemy_x
    enemy.rect.y = enemy_y
    enemies.add(enemy)

player = Player('ship.png', x=0, y=0, speed=5)
player_width = player.image.get_width()
player_height = player.image.get_height()

player.rect.x = (WIDTH - player_width) // 2
player.rect.y = HEIGHT - player_height - 10

scaled_width_player = player_width // 18
scaled_height_player = player_height // 18
player.image = pygame.transform.scale(player.image, (scaled_width_player, scaled_height_player))
player.rect = player.image.get_rect()
player.rect.x = (WIDTH - scaled_width_player) // 2
player.rect.y = HEIGHT - scaled_height_player - 10

# Группа для пуль
bullets = pygame.sprite.Group()

font = pygame.font.SysFont('Arial', 24)

missed = 0
destroyed = 0
game_over = False

while not game_over:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x = player.rect.x + (player.rect.width // 2)
                bullet_y = player.rect.y
                bullet = GameSprite('bullet.png', bullet_x, bullet_y)
                bullet.image = pygame.transform.scale(bullet.image, (10, 30))
                bullet.rect = bullet.image.get_rect()
                bullet.rect.x = bullet_x
                bullet.rect.y = bullet_y
                bullets.add(bullet)
                fire_sound.play()

    keys_pressed = pygame.key.get_pressed()
    player.update(keys_pressed)

    collision_tolerance = 2
    for enemy in enemies:
        enemy.update()
        if enemy.rect.y > HEIGHT:
            enemy.reset_position()
            missed += 1
        enemy_rect = enemy.rect.inflate(-collision_tolerance, -collision_tolerance)
        player_rect = player.rect.inflate(-collision_tolerance, -collision_tolerance)
        if enemy_rect.colliderect(player_rect):
            game_over = True
            result_text = 'Вы проиграли! (столкновение)'
            break

    for bullet in list(bullets):
        bullet.rect.y -= 10
        if bullet.rect.y < -bullet.rect.height:
            bullets.remove(bullet)

    for bullet in list(bullets):
        hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
        if hit_enemies:
            for enemy in hit_enemies:
                enemy.reset_position()
                destroyed += 1
            bullets.remove(bullet)

    window.blit(background, (0, 0))
    player.reset()

    for enemy in enemies:
        enemy.reset()

    for bullet in bullets:
        window.blit(bullet.image, (bullet.rect.x, bullet.rect.y))

    missed_text = font.render(f'Пропущено: {missed}', True, (255, 255, 255))
    window.blit(missed_text, (10, 10))
    destroyed_text = font.render(f'Сбито: {destroyed}', True, (255, 255, 255))
    window.blit(destroyed_text, (10, 40))

    pygame.display.update()

    if missed >= 3:
        game_over = True
        result_text = 'Вы проиграли! (пропущено 3 врага)'
    elif destroyed >= 10:
        game_over = True
        result_text = 'Вы выиграли!'

window.fill((0, 0, 0))
font_large = pygame.font.SysFont('Arial', 48)
if 'Вы проиграли' in result_text:
    final_message = font_large.render(result_text, True, (255, 0, 0))
else:
    final_message = font_large.render(result_text, True, (0, 255, 0))
window.blit(final_message, ((WIDTH - final_message.get_width()) // 2, (HEIGHT - final_message.get_height()) // 2))
pygame.display.update()
pygame.time.wait(3000)

pygame.quit()