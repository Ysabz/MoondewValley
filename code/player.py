import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.Surface((32, 64))
        self.image.fill('green')
        self.rect = self.image.get_rect(center=pos)

        # movement attributes
        self.dir = pygame.math.Vector2()
        # we use a different attribute for position because rect only store integer which does not work with delta time
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def input(self):
        keys = pygame.key.get_pressed()
        # vertical movement
        if keys[pygame.K_UP]:
            self.dir.y = -1
        elif keys[pygame.K_DOWN]:
            self.dir.y = 1
        else:
            self.dir.y = 0

        # horizontal movement
        if keys[pygame.K_LEFT]:
            self.dir.x = -1
        elif keys[pygame.K_RIGHT]:
            self.dir.x = 1
        else:
            self.dir.x = 0

    def update(self, dt):
        self.input()
        print(self.dir.x)

        # horizontal movement
        self.pos.x += dt * self.speed * self.dir.x
        self.rect.centerx = self.pos.x
        # vertical movement
        self.pos.y += dt * self.speed * self.dir.y
        self.rect.centery = self.pos.y
