import math
from math import sqrt

import pygame
import random
import os


class Settings(object):
    window_width = 1280
    window_height = 720
    fps = 60
    bubble_startsize = 10
    bubble_size = (5, 5)
    border = 10
    timeunit = 60
    path_image = os.path.join(os.path.dirname(__file__), "images")
    path_sound = os.path.join(os.path.dirname(__file__), "sounds")
    path_highscore = os.path.join(os.path.dirname(__file__), "highscore.txt")


class Background(object):
    def __init__(self, filename):
        self.image = pygame.image.load(os.path.join(Settings.path_image, filename))
        self.image = pygame.transform.scale(
            self.image, (Settings.window_width, Settings.window_height)
        )
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Bubble(pygame.sprite.Sprite):
    def __init__(self, filename, g):
        super().__init__()
        self.r = 10
        self.image_orig = pygame.image.load(
            os.path.join(Settings.path_image, filename)
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image_orig, (self.r * 2, self.r * 2))
        self.rect = self.image.get_rect()  # Hitbox
        self.find_position(g)
        self.t = 0
        self.spawnrate = 0
        self.scale = {"width": self.rect.width, "height": self.rect.height}
        self.scale_speed = random.randint(1, 4)

    def find_position(self, g):
        x1 = random.randint(
            self.r + Settings.border, Settings.window_width - self.r - Settings.border
        )
        y1 = random.randint(
            self.r + Settings.border, Settings.window_height - self.r - Settings.border
        )
        r1 = self.r
        if len(g.bubbles) <= 0:
            self.rect.center = (x1, y1)
            return
        for bubble in g.bubbles:
            x2 = bubble.rect.center[0]
            y2 = bubble.rect.center[1]
            r2 = bubble.r
            dist = math.sqrt(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2) - r1 - r2 + 10
            if dist > 0:
                self.rect.center = (x1, y1)
                return
        self.find_position(g)

    def update(self):
        self.scale["width"] += self.scale_speed
        self.scale["height"] += self.scale_speed
        c = self.rect.center
        self.image = pygame.transform.scale(
            self.image_orig, (self.scale["width"], self.scale["height"])
        )
        self.rect = self.image.get_rect()
        self.rect.center = c
        collision_bubbles = pygame.sprite.spritecollide(
            self, game.bubbles, False, pygame.sprite.collide_mask
        )
        if len(collision_bubbles) > 0:
            for bubble in collision_bubbles:
                if bubble != self:
                    collision_sound = pygame.mixer.Sound(
                        os.path.join(Settings.path_sound, "Collision.mp3")
                    )
                    pygame.mixer.Sound.play(collision_sound)
                    game.gameover = True


class Mouse(pygame.sprite.Sprite):
    def __init__(self, filename="Pinnadel2.png"):
        super().__init__()
        self.change_image(filename)

    def draw(self, screen):
        screen.blit(self.image, pygame.mouse.get_pos())

    def change_image(self, filename):
        self.image = pygame.image.load(
            os.path.join(Settings.path_image, filename)
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 35))
        self.rect = self.image.get_rect()


class Game(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Settings.window_width, Settings.window_height)
        )
        self.clock = pygame.time.Clock()
        self.running = True
        self.background = Background("underwater.jpg")
        self.mouse = Mouse()
        self.pause = False
        pygame.mouse.set_visible(False)
        self.bubbles = pygame.sprite.Group()
        self.t = 0
        self.t2 = 0
        self.font_normalsize = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.points = 0
        self.gameover = False

    def run(self):
        while self.running:
            self.clock.tick(Settings.fps)
            self.watch_for_events()
            self.draw()
            if not self.pause and not self.gameover:
                self.update()
            elif self.pause == True:
                self.paused()
            elif self.gameover == True:
                self.gameover_check()
            self.save_highscore()
            pygame.display.flip()

    def paused(self):
        screenfill = pygame.Surface((Settings.window_width, Settings.window_height))
        screenfill.fill((170, 170, 170))
        screenfill.set_alpha(180)
        self.screen.blit(screenfill, (0, 0))
        pause = self.font_normalsize.render("Paused", False, (255, 255, 255))
        score = self.font_normalsize.render(
            f"Highscore:{self.get_highscore()}", False, (255, 255, 255)
        )
        self.screen.blit(
            pause,
            (
                Settings.window_width // 2 - pause.get_width() // 2,
                Settings.window_height // 2 - pause.get_height() // 2,
            ),
        )
        self.screen.blit(
            score,
            (
                Settings.window_width // 2 - score.get_width() // 2,
                Settings.window_height // 2.1 - score.get_height() // 2.1,
            ),
        )

    def gameover_check(self):
        gameover_screenfill = pygame.Surface(
            (Settings.window_width, Settings.window_height)
        )
        gameover_screenfill.fill((170, 170, 170))
        gameover_screenfill.set_alpha(180)
        self.screen.blit(gameover_screenfill, (0, 0))
        gameover = self.font_normalsize.render("Game Over", False, (255, 255, 255))
        question = self.font_normalsize.render(
            "to restart the game press Space", False, (255, 255, 255)
        )
        gameover_score = self.font_normalsize.render(
            f"Points:{self.points}", False, (255, 255, 255)
        )
        self.screen.blit(
            gameover,
            (
                Settings.window_width // 2 - gameover.get_width() // 2,
                Settings.window_height // 2 - gameover.get_height() // 2,
            ),
        )
        self.screen.blit(
            question,
            (
                Settings.window_width // 2 - question.get_width() // 2,
                Settings.window_height // 2.1 - question.get_height() // 2.1,
            ),
        )
        self.screen.blit(
            gameover_score,
            (
                Settings.window_width // 2 - gameover_score.get_width() // 2,
                Settings.window_height // 2.2 - gameover_score.get_height() // 2.2,
            ),
        )

    def watch_for_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for bubble in self.bubbles:
                    hits = bubble.rect.collidepoint(*pygame.mouse.get_pos())
                    if hits == True:
                        burst_sound = pygame.mixer.Sound(
                            os.path.join(Settings.path_sound, "Burst.mp3")
                        )
                        pygame.mixer.Sound.play(burst_sound)
                        self.points += bubble.scale["width"] // 2
                        bubble.kill()
                if event.button == 3:
                    self.pause = not self.pause
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause = not self.pause
                if event.key == pygame.K_SPACE:
                    if self.gameover == True:
                        self.reset()

    def reset(self):
        self.points = 0
        self.bubbles.empty()
        self.gameover = False

    @staticmethod
    def get_highscore() -> int:
        with open(Settings.path_highscore, "r", encoding="utf8") as file:
            highscore = int(file.read())

        return highscore

    @staticmethod
    def set_highscore(highscore: int) -> None:
        with open(Settings.path_highscore, "w", encoding="utf8") as file:
            file.write(str(highscore))

    def save_highscore(self) -> None:
        if self.points > Game.get_highscore():
            Game.set_highscore(self.points)

    def update(self):
        self.t += 1
        if self.t >= Settings.timeunit:
            self.t = 0
            if (
                len(self.bubbles)
                <= (Settings.window_width + Settings.window_height) / 100
            ):
                self.bubbles.add(Bubble("bubble.png", self))
                spawn_sound = pygame.mixer.Sound(
                    os.path.join(Settings.path_sound, "spawn.mp3")
                )
                pygame.mixer.Sound.play(spawn_sound)
        self.t2 += 1
        if self.t2 >= Settings.timeunit / 2:
            self.t2 = 0
            self.bubbles.update()
        bubble_is_hovered = False
        for bubble in self.bubbles:
            hits = bubble.rect.collidepoint(*pygame.mouse.get_pos())
            if hits == True:
                bubble_is_hovered = True
        if bubble_is_hovered == True:
            self.mouse.change_image("Pinnadel.png")
        else:
            self.mouse.change_image("Pinnadel2.png")
        self.mouse.update()
        self.mouse.draw(self.screen)

    def draw(self):
        self.background.draw(self.screen)
        self.bubbles.draw(self.screen)
        self.mouse.draw(self.screen)
        points = self.font_normalsize.render(
            f"Points: {self.points}", False, (255, 255, 255)
        )
        self.screen.blit(points, (0, 10))


if __name__ == "__main__":
    game = Game()
    game.run()
