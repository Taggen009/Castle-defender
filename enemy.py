import pygame

class Enemy(pygame.sprite.Sprite):
	def __init__(self, health, animation_list, x, y, speed, level, damage, money):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.speed = speed + level // 100
		self.health = health
		self.damage = damage
		self.money = money
		self.last_attack = pygame.time.get_ticks()
		self.attack_cooldown = 1000
		self.animation_list = animation_list
		self.frame_index = 0
		self.action = 0 #0: walk, 1: attack, 2: death
		self.update_time = pygame.time.get_ticks()

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.mask = pygame.mask.from_surface(self.image)


	def update(self, surface, target, fireball_group):
		if self.alive == True:

			if pygame.sprite.spritecollide(self, fireball_group, True):
				
				self.health -= 25

		
			if self.rect.right > target.rect.left and self.action != 2:
				self.update_action(1)
			
				
			if self.action == 0:

				self.rect.x += self.speed	

			if self.action == 1:

				if pygame.time.get_ticks() - self.last_attack > self.attack_cooldown:
					target.health -= self.damage
					if target.health < 0:
						target.health = 0
					self.last_attack = pygame.time.get_ticks()	

			if self.health <= 0:
				target.money += self.money
				target.score += 100
				self.update_action(2)	
				self.alive = False

		self.update_animations()



		surface.blit(self.image, self.rect)	


	def update_animations(self):

		animation_cooldown = 100

		self.image = self.animation_list[self.action][self.frame_index]

		if pygame.time.get_ticks() - self.update_time > animation_cooldown:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 2:
				self.frame_index = len(self.animation_list[self.action]) - 1

			else:	
				self.frame_index = 0

	def update_action(self, new_action):

		if new_action != self.action:
			self.action = new_action

			self.frame_index
			self.update_date = pygame.time.get_ticks()
					