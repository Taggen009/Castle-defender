import pygame
import math
import random
import os
from enemy import Enemy
from button import Button


pygame.init()


screen_width = 800 
screen_height = 600

white = (255, 255, 255)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Castle Defender')

clock = pygame.time.Clock()
fps = 60

level = 1
level_difficulty = 0
target_difficulty = 1000
difficulty_multiplier = 1.1
game_over = False
next_level = False
enemy_timer = 1000 - level * 5
last_enemy = pygame.time.get_ticks()
enemies_alive = 0
tower_cost = 5000
high_score = 0
tower_positions = [
[screen_width - 280, screen_height - 220],
[screen_width - 100, screen_height - 220],
]


if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())


font = pygame.font.SysFont('Futura', 30)
font_60 = pygame.font.SysFont('Futura', 60)


white = (255, 255, 255)
grey = (100, 100, 100)

bg = pygame.image.load('img/bg.png').convert_alpha()

castle_img_100 = pygame.image.load('img/castle/castle_100.png').convert_alpha()
castle_img_50 = pygame.image.load('img/castle/castle_50.png').convert_alpha()
castle_img_25 = pygame.image.load('img/castle/castle_25.png').convert_alpha()

tower_img_100 = pygame.image.load('img/tower/tower_100.png').convert_alpha()
tower_img_50 = pygame.image.load('img/tower/tower_50.png').convert_alpha()

fireball_img = pygame.image.load('img/fireball.png').convert_alpha()
f_w = fireball_img.get_width()
f_h = fireball_img.get_height()
fireball_img = pygame.transform.scale(fireball_img, (int(f_w * 0.5), int(f_h * 0.5)))

enemy_animations = []
enemy_types = ['goblin', 'goblin_red', 'goblin_purple', 'orc', 'orc_red', 'orc_purple']
enemy_health = [75, 125, 200, 500, 750, 1500]


animation_types = ['walk', 'attack', 'death']
for enemy in enemy_types:

	animation_list = []
	for animation in animation_types:

		temp_list = []

		num_of_frames = 6
		for i in range(num_of_frames):
			img = pygame.image.load(f'img/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
			e_w = img.get_width()
			e_h = img.get_height()
			img = pygame.transform.scale(img, (int(e_w * 1.2), int(e_h * 1.2)))
			temp_list.append(img)
		animation_list.append(temp_list)
	enemy_animations.append(animation_list)


repair_img = pygame.image.load('img/repair.png').convert_alpha()

armour_img = pygame.image.load('img/armour.png').convert_alpha()


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def show_info():
	draw_text('Money: ' + str(castle.money), font, grey, 10, 10)
	draw_text('Score: ' + str(castle.score), font, grey, 180, 10)
	draw_text('High Score: ' + str(high_score), font, grey, 180, 30)
	draw_text('Level: ' + str(level), font, grey, screen_width // 2, 10)
	draw_text('Health: ' + str(castle.health) + " / " + str(castle.max_health), font, grey, screen_width - 230, screen_height - 50)
	draw_text('1000', font, grey, screen_width - 220, 75)
	draw_text(f'{castle.upgrade_amount}', font, grey, screen_width - 60 , 75)
	if len(tower_group) < 2:
		draw_text('5000', font, grey, screen_width - 140, 80)
	else:
		draw_text('MAX', font, grey, screen_width - 140, 80)	
    


class Castle():
	def __init__(self, image100, image50, image25, x, y, scale):
		self.health = 1000
		self.max_health = self.health
		self.fired = False
		self.money = 0
		self.score = 0
		self.upgrade_amount = 1000

		width = image100.get_width()
		height = image100.get_height()

		self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
		self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
		self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))

		self.rect = self.image100.get_rect()
		self.rect.x = x
		self.rect.y = y


	def shoot(self):
		pos = pygame.mouse.get_pos()
		x_dist = pos[0] - self.rect.midleft[0] - 50 
		y_dist = -(pos[1] - self.rect.midleft[1])
		self.angle = math.degrees(math.atan2(y_dist, x_dist))

		if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 70:
			self.fired = True
			fireball = Fireball(fireball_img, self.rect.midleft[0] + 50, self.rect.midleft[1], self.angle)
			fireball_group.add(fireball)

		if 	pygame.mouse.get_pressed()[0] == False:
			self.fired = False



	def draw(self):

		if self.health <= 250:
			self.image = self.image25
		elif self.health <= 500:
			self.image = self.image50
		else:
			self.image = self.image100		

		screen.blit(self.image, self.rect)


	def repair(self):
		if self.money >= 1000 and self.health < self.max_health:
			self.health += 500
			self.money -= 1000
		if self.health > self.max_health:
			self.health = self.max_health 


	def upgrade(self):
		if self.money >= self.upgrade_amount:
			self.max_health += 500
			self.health += 500
			self.money -= self.upgrade_amount
			self.upgrade_amount += 500
			


class Tower(pygame.sprite.Sprite):
	def __init__(self, image100, image50, x, y, scale):
		pygame.sprite.Sprite.__init__(self)

		self.target_acquired = False
		self.angle = 0
		self.last_shot = pygame.time.get_ticks()

		width = image100.get_width()
		height = image100.get_height()

		self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
		self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
		self.image = self.image100
		self.rect = self.image100.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, enemy_group):
		self.target_acquired = False
		for e in enemy_group:
			if e.alive:	
				target_x, target_y = e.rect.center
				self.target_acquired = True
				break
		if self.target_acquired:		

			x_dist = target_x - self.rect.midleft[0] - 40 
			y_dist = -(target_y - self.rect.midleft[1])
			self.angle = math.degrees(math.atan2(y_dist, x_dist))

			shot_cooldown = 750

			if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
				self.last_shot = pygame.time.get_ticks()
				fireball = Fireball(fireball_img, self.rect.midleft[0] + 50, self.rect.midleft[1], self.angle)
				fireball_group.add(fireball)


		if castle.health <= 250:
			self.image = self.image50
		else:
			self.image = self.image100			



class Fireball(pygame.sprite.Sprite):
	def __init__(self, image, x, y, angle):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x	
		self.rect.y = y
		self.angle = math.radians(angle)
		self.speed = 10

		self.dx = math.cos(self.angle) * self.speed
		self.dy = -(math.sin(self.angle) * self.speed)

	def update(self):
		
		if self.rect.right < 0 or self.rect.left > screen_width or self.rect.bottom < 0 or self.rect.top > screen_height:
			self.kill()

		self.rect.x += self.dx	
		self.rect.y += self.dy


class Crosshair():
	def __init__(self, scale):
		image = pygame.image.load('img/crosshair.png').convert_alpha()
		width = image.get_width()
		height = image.get_height()

		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()

		pygame.mouse.set_visible(False)

	def draw(self):
		mx, my = pygame.mouse.get_pos()
		self.rect.center = (mx, my)
		screen.blit(self.image, self.rect)	


castle = Castle(castle_img_100, castle_img_50, castle_img_25, screen_width - 200, screen_height - 350, 1.2)	

crosshair = Crosshair(0.5)

repair_button = Button(screen_width - 240, 10, repair_img, 0.06)
armour_button = Button(screen_width - 65, 10, armour_img, 0.06)
tower_button = Button(screen_width - 140, 10, tower_img_100, 0.6)

tower_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


run = True
while run:

	clock.tick(fps)
	

	if game_over == False:
		screen.blit(bg, (0, 0))

		castle.draw()
		castle.shoot()

		tower_group.draw(screen)
		tower_group.update(enemy_group)

		crosshair.draw()

		fireball_group.update()
		fireball_group.draw(screen)

		enemy_group.update(screen, castle, fireball_group)


		show_info()

		if repair_button.draw(screen):
			castle.repair()
		if tower_button.draw(screen):
			if castle.money >= tower_cost and len(tower_group) < 2:
				tower = Tower(
				tower_img_100,
				tower_img_50,
				tower_positions[len(tower_group)][0],
				tower_positions[len(tower_group)][1],
				1.2)
				tower_group.add(tower)
				castle.money -= tower_cost

		if armour_button.draw(screen):
			castle.upgrade()

		if level_difficulty < target_difficulty and level < 5:
			if pygame.time.get_ticks() - last_enemy > enemy_timer:

				e = random.randint(0, len(enemy_types) - 4)

				enemy = Enemy(enemy_health[e], enemy_animations[e], -100, screen_height - 100, 1, level, 25, 100)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += enemy_health[e]

		if level_difficulty < target_difficulty and level == 5:	
			if pygame.time.get_ticks() - last_enemy > enemy_timer:


				enemy = Enemy(enemy_health[3], enemy_animations[3], -100, screen_height - 100, 1, level, 50, 200)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += 10000000

		
		if level_difficulty < target_difficulty and level == 10:	
			if pygame.time.get_ticks() - last_enemy > enemy_timer:


				enemy = Enemy(enemy_health[4], enemy_animations[4], -100, screen_height - 100, 1, level, 75, 300)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += 10000000

		if level_difficulty < target_difficulty and level == 15:	
			if pygame.time.get_ticks() - last_enemy > enemy_timer:


				enemy = Enemy(enemy_health[5], enemy_animations[5], -100, screen_height - 150, 1, level, 100, 500)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += 10000000				

		if level_difficulty < target_difficulty:
			if pygame.time.get_ticks() - last_enemy > enemy_timer and level > 5 and level < 10:

				e = random.randint(0, len(enemy_types) - 3)

				enemy = Enemy(enemy_health[e], enemy_animations[e], -100, screen_height - 100, 1, level, 25, 200)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += enemy_health[e]

		if level_difficulty < target_difficulty:
			if pygame.time.get_ticks() - last_enemy > enemy_timer and level > 10 and level < 15:

				e = random.randint(0, len(enemy_types) - 2)

				enemy = Enemy(enemy_health[e], enemy_animations[e], -100, screen_height - 100, 1, level, 25, 300)
				enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += enemy_health[e]	

		if level_difficulty < target_difficulty:
			if pygame.time.get_ticks() - last_enemy > enemy_timer and level > 15:

				e = random.randint(0, len(enemy_types) - 1)

				if e == 5:
					enemy = Enemy(enemy_health[5], enemy_animations[5], -100, screen_height - 150, 1, level, 200, 500)

				else:
					enemy = Enemy(enemy_health[e], enemy_animations[e], -100, screen_height - 100, 1, level, 300)
					enemy_group.add(enemy)

				last_enemy = pygame.time.get_ticks()

				level_difficulty += enemy_health[e]							

		if level_difficulty >= target_difficulty:
			
			enemies_alive = 0
			for e in enemy_group:
				if e.alive == True:
					enemies_alive += 1

			if enemies_alive == 0 and next_level == False:
				next_level = True
				level_reset_time = pygame.time.get_ticks()

		if next_level == True:
			draw_text('LEVEL COMPLETE!!', font_60, white, 200, 300)

			if castle.score > high_score:
				high_score = castle.score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))

			if pygame.time.get_ticks() - level_reset_time > 1500:
				next_level = False
				level += 1
				last_enemy = pygame.time.get_ticks()
				target_difficulty *= difficulty_multiplier
				level_difficulty = 0
				enemy_group.empty()	

		if castle.health <= 0:
			game_over = True

	else:
		draw_text('GAME OVER!', font, grey, 300, 300)
		draw_text('PRESS "A" TO PLAY AGAIN!', font, grey, 250, 360)	
		pygame.mouse.set_visible(True)
		key =pygame.key.get_pressed()
		if key[pygame.K_a]:

			game_over = False
			level = 1
			target_difficulty = 1000
			level_difficulty = 0
			last_enemy = pygame.time.get_ticks()
			enemy_group.empty()
			tower_group.empty()
			castle.score = 0
			castle.health = 1000
			castle.max_health = 1000
			castle.money = 0
			pygame.mouse.set_visible(False)	

							
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()		

pygame.quit()			