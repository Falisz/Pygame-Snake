import pygame
import os
import random
import sys

# CONSTANTS
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CELL_SIZE = 80
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE
FPS = 6
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (50, 155, 0)
GOLD = (255, 215, 0)

# SPRITE ASSETS
assets_path = os.path.join(os.getcwd(), 'assets')
# print(assets_path)
SNAKE_SPRITES = {}
for file_name in sorted(os.listdir(os.path.join(assets_path, 'snake'))):
    image_name = file_name[6:-4].upper()
    SNAKE_SPRITES[image_name] = pygame.image.load(os.path.join(assets_path, 'snake', file_name))
CELL_SPRITES = {}
for file_name in sorted(os.listdir(os.path.join(assets_path, 'level'))):
    image_name = file_name[:-4].upper()
    CELL_SPRITES[image_name] = pygame.image.load(os.path.join(assets_path, 'level', file_name))
APPLE_SPRITES = {}
for file_name in sorted(os.listdir(os.path.join(assets_path, 'apple'))):
    image_name = file_name[:-4].upper()
    APPLE_SPRITES[image_name] = pygame.image.load(os.path.join(assets_path, 'apple', file_name))
# print(SNAKE_SPRITES)
# print(CELL_SPRITES)
# print(APPLE_SPRITES)

# MUSIC ASSETS:
background_music = os.path.join(os.getcwd(), 'assets', 'vlad-8_bit_snake.mp3')
arcade_music = os.path.join(os.getcwd(), 'assets', 'slow_ethereal_sequencer.mp3')
sound_apple = os.path.join(os.getcwd(), 'assets', 'apple_eaten.mp3')
sound_death = os.path.join(os.getcwd(), 'assets', 'death_sound.mp3')
sound_start = os.path.join(os.getcwd(), 'assets', 'level_start.mp3')
sound_level_up = os.path.join(os.getcwd(), 'assets', 'level_up.mp3')

class Level:
    def __init__(self, level_number, level_map, snake_x=None, snake_y=None, score=0, score_to_level_up=5, next_level=None, golden_apple_chance=0.2,
                 shrink_apple_chance=0.15, wither_apple_chance=0.1, apples_number=1):
        self.level_number = level_number
        self.map = level_map
        self.snake_x = snake_x
        self.snake_y = snake_y
        self.snake = Snake(self.snake_x or GRID_WIDTH // 2, self.snake_y or GRID_HEIGHT // 2)
        self.score = score
        self.score_to_level_up = score_to_level_up
        self.next_level = next_level
        self.level_music = pygame.mixer.Sound(background_music)
        self.golden_apple_chance = golden_apple_chance
        self.shrink_apple_chance = shrink_apple_chance
        self.wither_apple_chance = wither_apple_chance
        self.apples_number = apples_number
        self.apples = []
        self.apples_clock = 0
        self.apples_timer = 300
        self.spawn_apples()

    def is_final_level(self):
        return self.next_level is None

    def spawn_apples(self):
        self.apples.clear()
        self.apples_clock = 0
        for _ in range(random.randint(1, self.apples_number)):
            if random.random() <= self.golden_apple_chance:
                self.apples.append(GoldenApple(self))
            elif random.random() <= self.shrink_apple_chance:
                self.apples.append(ShrinkingApple(self))
            elif random.random() <= self.wither_apple_chance:
                self.apples.append(WitheredApple(self))
            else:
                self.apples.append(Apple(self))

    def draw_score(self):
        font = pygame.font.SysFont("Roboto", 40)
        score_text = font.render("Score: " + str(self.score), True, WHITE)
        score_rect = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10))
        score_rect.set_alpha(160)
        score_rect.fill((0, 0, 0))
        score_rect.blit(score_text, (10, 5))
        window.blit(score_rect, (WINDOW_WIDTH - score_rect.get_width() - 15, 0 + 15))

    def draw_level(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                sprite = self.map[y][x].sprite
                window.blit(sprite, (x * CELL_SIZE, y * CELL_SIZE))

        font = pygame.font.SysFont("Roboto", 40)
        level_text = font.render("Level: " + str(self.level_number), True, WHITE)
        level_rect = pygame.Surface((level_text.get_width() + 20, level_text.get_height() + 10))
        level_rect.set_alpha(160)
        level_rect.fill((0, 0, 0))
        level_rect.blit(level_text, (10, 5))
        window.blit(level_rect, (15, 15))

        font = pygame.font.SysFont("Roboto", 20)
        goal_text = font.render("Goal to the next level: " + str(self.score_to_level_up) + " points", True, WHITE)
        goal_rect = pygame.Surface((goal_text.get_width() + 20, goal_text.get_height() + 10))
        goal_rect.set_alpha(160)
        goal_rect.fill((0, 0, 0))
        goal_rect.blit(goal_text, (10, 5))
        window.blit(goal_rect,
                    (WINDOW_WIDTH // 2 - goal_rect.get_width() // 2, WINDOW_HEIGHT - 15 - goal_rect.get_height()))

    def draw_apples(self):
        for apple in self.apples:
            apple.draw()

    def game_over(self, message=None, button_text=None):
        self.level_music.stop()
        game_over_sound.play()
        game_over_sound.set_volume(0.5)
        MenuScreen("Game Over!", message, button_text or "Replay the level!", "Exit the game!", "exit").show()

    def level_up(self):
        self.level_music.stop()
        level_up_sound.play()
        level_up_sound.set_volume(0.4)

    def start(self, start_score=None):
        self.spawn_apples()
        self.draw_apples()
        self.snake.restart(self.snake_x, self.snake_y)
        self.score = start_score or 0
        level_start.play()
        level_start.set_volume(0.6)
        self.level_music.play()
        self.level_music.set_volume(0.15)


class ArcadeLevel(Level):
    def __init__(self, level_number, level_map, snake_x, snake_y, golden_apple_chance=None,
                 shrink_apple_chance=None, wither_apple_chance=None, apples_number=False):
        super().__init__(level_number, level_map, snake_x, snake_y, 0, -1, golden_apple_chance=golden_apple_chance,
                         shrink_apple_chance=shrink_apple_chance, wither_apple_chance=wither_apple_chance, apples_number=apples_number)
        self.snake_x = snake_x
        self.snake_y = snake_y
        self.level_music = pygame.mixer.Sound(arcade_music)
        self.apples_timer = 150

    def draw_level(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                sprite = self.map[y][x].sprite
                window.blit(sprite, (x * CELL_SIZE, y * CELL_SIZE))

        font = pygame.font.SysFont("Roboto", 40)
        level_text = font.render("Arcade Mode", True, WHITE)
        level_rect = pygame.Surface((level_text.get_width() + 20, level_text.get_height() + 10))
        level_rect.set_alpha(160)
        level_rect.fill((0, 0, 0))
        level_rect.blit(level_text, (10, 5))
        window.blit(level_rect, (15, 15))


class Cell:
    def __init__(self, cell_type="empty", sprite=CELL_SPRITES['GRASS']):
        self.cell_type = cell_type
        self.sprite = sprite

    def __repr__(self):
        return f"Cell: {self.cell_type}"


class Snake(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.head = SnakeSegment(x, y, "head", "down")
        self.segments = []
        self.tail = SnakeSegment(x, y-1, "tail", "down")
        self.grow_count = 0

    def update(self, keys):
        if keys[pygame.K_UP] and self.head.direction_towards != "down":
            self.head.direction_towards = "up"
        elif keys[pygame.K_DOWN] and self.head.direction_towards != "up":
            self.head.direction_towards = "down"
        elif keys[pygame.K_LEFT] and self.head.direction_towards != "right":
            self.head.direction_towards = "left"
        elif keys[pygame.K_RIGHT] and self.head.direction_towards != "left":
            self.head.direction_towards = "right"

        if self.head.direction_towards == "up":
            self.head.y -= 1
        elif self.head.direction_towards == "down":
            self.head.y += 1
        elif self.head.direction_towards == "left":
            self.head.x -= 1
        elif self.head.direction_towards == "right":
            self.head.x += 1

        if len(self.segments) > 0:
            last_direction = self.segments[0].direction_towards
        else:
            last_direction = self.tail.direction_towards

        if self.head.direction_towards != last_direction:
            if self.head.direction_towards == "up":
                if last_direction == "left":
                    self.segments.insert(0, SnakeSegment(self.head.x, self.head.y + 1, "turn", "up", "right"))
                elif last_direction == "right":
                    self.segments.insert(0, SnakeSegment(self.head.x, self.head.y + 1, "turn", "up", "left"))
            elif self.head.direction_towards == "down":
                if last_direction == "left":
                    self.segments.insert(0, SnakeSegment(self.head.x, self.head.y - 1, "turn", "down", "right"))
                elif last_direction == "right":
                    self.segments.insert(0, SnakeSegment(self.head.x, self.head.y - 1, "turn", "down", "left"))
            elif self.head.direction_towards == "left":
                if last_direction == "up":
                    self.segments.insert(0, SnakeSegment(self.head.x + 1, self.head.y, "turn", "left", "down"))
                elif last_direction == "down":
                    self.segments.insert(0, SnakeSegment(self.head.x + 1, self.head.y, "turn", "left", "up"))
            elif self.head.direction_towards == "right":
                if last_direction == "up":
                    self.segments.insert(0, SnakeSegment(self.head.x - 1, self.head.y, "turn", "right", "down"))
                elif last_direction == "down":
                    self.segments.insert(0, SnakeSegment(self.head.x - 1, self.head.y, "turn", "right", "up"))
        else:
            if self.head.direction_towards == "up":
                self.segments.insert(0, SnakeSegment(self.head.x, self.head.y + 1, "body", self.head.direction_towards))
            elif self.head.direction_towards == "down":
                self.segments.insert(0, SnakeSegment(self.head.x, self.head.y - 1, "body", self.head.direction_towards))
            elif self.head.direction_towards == "left":
                self.segments.insert(0, SnakeSegment(self.head.x + 1, self.head.y, "body", self.head.direction_towards))
            elif self.head.direction_towards == "right":
                self.segments.insert(0, SnakeSegment(self.head.x - 1, self.head.y, "body", self.head.direction_towards))

        if self.grow_count > 0:
            self.grow_count -= 1
        elif len(self.segments) > 0:
            if self.grow_count < 0:
                self.grow_count += 1
                if len(self.segments) > 2:
                    self.tail.x = self.segments[-2].x
                    self.tail.y = self.segments[-2].y
                    self.tail.direction_towards = self.segments[-2].direction_towards
                    self.segments.pop()
                    self.segments.pop()
            else:
                self.tail.x = self.segments[-1].x
                self.tail.y = self.segments[-1].y
                self.tail.direction_towards = self.segments[-1].direction_towards
                self.segments.pop()
        else:
            self.tail.x = self.head.x
            self.tail.y = self.head.y
            self.tail.direction_towards = self.head.direction_towards
            if self.head.direction_towards == "up":
                self.tail.y += 1
            elif self.head.direction_towards == "down":
                self.tail.y -= 1
            elif self.head.direction_towards == "left":
                self.tail.x += 1
            elif self.head.direction_towards == "right":
                self.tail.x -= 1

    def grow(self, amount):
        self.grow_count += amount

    def restart(self, x, y):
        self.head = SnakeSegment(x, y, "head", "down")
        self.segments = []
        self.tail = SnakeSegment(x, -y, "tail", "down")
        self.grow_count = 0

    def draw(self):
        self.head.kill()
        self.tail.kill()
        for segment in self.segments:
            segment.kill()
        window.blit(self.tail.get_sprite(), (self.tail.x * CELL_SIZE, self.tail.y * CELL_SIZE))
        for segment in self.segments:
            window.blit(segment.get_sprite(), (segment.x * CELL_SIZE, segment.y * CELL_SIZE))
        window.blit(self.head.get_sprite(), (self.head.x * CELL_SIZE, self.head.y * CELL_SIZE))


class SnakeSegment(pygame.sprite.Sprite):
    def __init__(self, x, y, segment_type, dir_to=None, dir_from=None):
        super().__init__()
        self.x = x
        self.y = y
        self.segment_type = segment_type
        self.direction_towards = dir_to
        self.direction_from = dir_from

    def get_sprite(self):
        if self.segment_type != "turn":
            return SNAKE_SPRITES[f"{self.segment_type.upper()}-{self.direction_towards.upper()}"]
        else:
            return SNAKE_SPRITES[f"TURN-{self.direction_towards.upper()}-{self.direction_from.upper()}"]


class Apple(pygame.sprite.Sprite):
    def __init__(self, level=None,):
        super().__init__()
        self.level = level
        self.x = 0
        self.y = 0
        self.randomize()

    def eat_effect(self):
        self.level.score += 1
        self.level.snake.grow_count += 1

    def randomize(self):
        while True:
            self.x = random.randint(0, GRID_WIDTH - 1)
            self.y = random.randint(0, GRID_HEIGHT - 1)
            respawn = False
            for seg in self.level.snake.segments:
                if self.x == seg.x and self.y == seg.y:
                    respawn = True
            if self.x == self.level.snake.head.x and self.y == self.level.snake.head.y:
                respawn = True
            if self.x == self.level.snake.tail.x and self.y == self.level.snake.tail.y:
                respawn = True
            for apple in self.level.apples:
                if self.x == apple.x and self.y == apple.y:
                    respawn = True
            if not isinstance(self.level.map[self.y][self.x], Cell) or self.level.map[self.y][self.x].cell_type == "wall":
                respawn = True
            if not respawn:
                break

    def draw(self):
        window.blit(APPLE_SPRITES["APPLE"], (self.x * CELL_SIZE, self.y * CELL_SIZE))


class GoldenApple(Apple):
    def __init__(self, level):
        super().__init__(level)

    def eat_effect(self):
        if isinstance(self.level, ArcadeLevel):
            self.level.score += random.randint(2, 5) * random.randint(1, 5)
            self.level.snake.grow_count += 1
        else:
            self.level.score += random.randint(2, 5)
            self.level.snake.grow_count += 2

    def draw(self):
        window.blit(APPLE_SPRITES["APPLE_GOLDEN"], (self.x * CELL_SIZE, self.y * CELL_SIZE))


class ShrinkingApple(Apple):
    def __init__(self, level):
        super().__init__(level)

    def eat_effect(self):
        if isinstance(self.level, ArcadeLevel):
            self.level.score += random.randint(1, 3) * random.randint(1, 3)
            self.level.snake.grow_count -= 10
        else:
            self.level.score += random.randint(1, 3)
            self.level.snake.grow_count -= 5

    def draw(self):
        window.blit(APPLE_SPRITES["APPLE_SHRINK"], (self.x * CELL_SIZE, self.y * CELL_SIZE))


class WitheredApple(Apple):
    def __init__(self, level):
        super().__init__(level)

    def eat_effect(self):
        if isinstance(self.level, ArcadeLevel):
            self.level.score -= random.randint(2, 6)
        else:
            self.level.score -= random.randint(1, 5)
        if self.level.score < 0:
            self.level.score = 0
        self.level.snake.grow_count += 1

    def draw(self):
        window.blit(APPLE_SPRITES["APPLE_WITHERED"], (self.x * CELL_SIZE, self.y * CELL_SIZE))


class MenuScreen:
    def __init__(self, title="Insert title here!", subtitle: str = "", button1=None, button2=None,
                 escape_behaviour="continue"):
        self.title = title
        self.subtitle = subtitle
        self.button1 = button1
        self.button2 = button2
        self.escape_behaviour = escape_behaviour

    def show(self):
        font_title = pygame.font.SysFont("Roboto", 120)
        font_subtitle = pygame.font.SysFont("Roboto Bold", 40)
        font_button = pygame.font.SysFont("Roboto", 30)

        while True:
            fill_color = (0, 0, 0)
            alpha = 200
            fill_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            fill_surface.fill((*fill_color, alpha))
            window.blit(fill_surface, (0, 0))
            title = font_title.render(self.title, True, GOLD)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 175))
            window.blit(title, title_rect)
            button_1, button_2 = None, None

            if self.subtitle != "":
                subtitle = font_subtitle.render(self.subtitle, True, WHITE)
                subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 70))
                window.blit(subtitle, subtitle_rect)

            if self.button1:
                button_1 = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, 300, 50)
                pygame.draw.rect(window, GREEN, button_1)
                button_1_text = font_button.render(self.button1, True, WHITE)
                button_1_text_rect = button_1_text.get_rect(center=button_1.center)
                window.blit(button_1_text, button_1_text_rect)

            if self.button2:
                button_2 = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 120, 300, 50)
                pygame.draw.rect(window, RED, button_2)
                button_2_text = font_button.render(self.button2, True, WHITE)
                button_2_text_rect = button_2_text.get_rect(center=button_2.center)
                window.blit(button_2_text, button_2_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.escape_behaviour == "continue":
                            return
                        elif self.escape_behaviour == "exit":
                            pygame.quit()
                            exit()
                    elif event.key == pygame.K_SPACE:
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_1 and button_1.collidepoint(mouse_pos):
                        return
                    elif button_2 and button_2.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()
            pygame.display.update()
            clock.tick(FPS)


map_1 = [
    [Cell("wall", CELL_SPRITES['WALL-SIDE-N-W'])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-N']) for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-N-E'])]]
for _ in range(7):
    map_1.append([Cell("wall", CELL_SPRITES['WALL-SIDE-E-W'])] + [Cell() for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-W-E'])])
map_1.append(
    [Cell("wall", CELL_SPRITES['WALL-SIDE-S-W'])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-N-S']) for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-S-E'])])
map_1[3][3], map_1[5][12] = (Cell("wall", CELL_SPRITES['OBSTACLE']) for _ in range(2))

map_2 = [
    [Cell("wall", CELL_SPRITES["WALL-BACKGROUND"]) for _ in range(7)] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-N']) for
                                                                         _ in range(7)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-N-E'])] + [Cell("wall", CELL_SPRITES["WALL-BACKGROUND"])],
    [Cell("wall", CELL_SPRITES['WALL-SIDE-N-W'])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-N']) for _ in range(6)] + [
        Cell() for _ in range(7)] + [Cell("wall", CELL_SPRITES['WALL-SIDE-W-E'])] + [
        Cell("wall", CELL_SPRITES["WALL-BACKGROUND"])]
]
for _ in range(5):
    map_2.append([Cell("wall", CELL_SPRITES['WALL-SIDE-E-W'])] + [Cell() for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-W-E'])])
map_2.append(
    [Cell("wall", CELL_SPRITES["WALL-BACKGROUND"])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-E-W'])] + [Cell() for _ in
                                                                                                       range(7)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-N-S']) for _ in range(6)] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-E'])])
map_2.append([Cell("wall", CELL_SPRITES["WALL-BACKGROUND"])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-W'])] + [
    Cell("wall", CELL_SPRITES['WALL-SIDE-N-S']) for _ in range(7)] + [Cell("wall", CELL_SPRITES["WALL-BACKGROUND"]) for
                                                                      _ in range(7)])

map_3 = [
    [Cell("wall", CELL_SPRITES["WALL-1"]) for _ in range(16)],
    [Cell("wall", CELL_SPRITES["WALL-1"]) for _ in range(2)] + [Cell("empty", CELL_SPRITES["FLOOR-1"]) for _ in
                                                                range(12)] + [Cell("wall", CELL_SPRITES["WALL-1"]) for _
                                                                              in range(2)]
]
for _ in range(5):
    map_3.append(
        [Cell("wall", CELL_SPRITES["WALL-1"])] + [Cell("empty", CELL_SPRITES["FLOOR-1"]) for _ in range(14)] + [
            Cell("wall", CELL_SPRITES["WALL-1"])])
map_3.append([Cell("wall", CELL_SPRITES["WALL-1"]) for _ in range(2)] + [Cell("empty", CELL_SPRITES["FLOOR-1"]) for _ in
                                                                         range(12)] + [
                 Cell("wall", CELL_SPRITES["WALL-1"]) for _ in range(2)])
map_3.append([Cell("wall", CELL_SPRITES["WALL-1"]) for _ in range(16)])

map_4 = [
    [Cell("wall", CELL_SPRITES['WALL-SIDE-N-W'])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-S-N']) for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-N-E'])]]
for _ in range(7):
    map_4.append([Cell("wall", CELL_SPRITES['WALL-SIDE-E-W'])] + [Cell() for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-W-E'])])
map_4.append(
    [Cell("wall", CELL_SPRITES['WALL-SIDE-S-W'])] + [Cell("wall", CELL_SPRITES['WALL-SIDE-N-S']) for _ in range(14)] + [
        Cell("wall", CELL_SPRITES['WALL-SIDE-S-E'])])
map_4[3][3], map_4[5][12], map_4[5][3], map_4[3][12], map_4[3][6], map_4[5][6], map_4[3][9], map_4[5][9] = (Cell("wall", CELL_SPRITES['OBSTACLE']) for _ in range(8))


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Snake Game")
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    apple_sound = pygame.mixer.Sound(sound_apple)
    game_over_sound = pygame.mixer.Sound(sound_death)
    level_start = pygame.mixer.Sound(sound_start)
    level_up_sound = pygame.mixer.Sound(sound_level_up)

    MenuScreen("Snake", "by Falisz, 2023", "Play!", "Exit!").show()

    selected_level = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    start_points = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    level_1 = Level(1, map_1, 8, 1, start_points, 10, None)
    level_2 = Level(2, map_2, 10, 2, start_points, 20, None)
    level_3 = Level(3, map_3, 8, 4, start_points, 40, None, 0.6, 0.7, 0.15)
    level_4 = Level(4, map_2, 10, 2, start_points, 60, None, 0.2, 0.2, 0.7, 2)
    level_5 = Level(5, map_4, 8, 2, start_points, 80, None, 0.25, 0.25, 0.5, 2)
    level_1.next_level = level_2
    level_2.next_level = level_3
    level_3.next_level = level_4
    level_4.next_level = level_5
    level_0 = ArcadeLevel(0, map_1, 8, 4, 0.5, 0.9, 0.1, 4)
    levels = {
        1: level_1,
        2: level_2,
        3: level_3,
        4: level_4,
        5: level_5,
        0: level_0
    }
    current_level = levels[selected_level]

    window.fill(BLACK)
    level_start.play()
    level_start.set_volume(0.5)
    current_level.level_music.play()
    current_level.level_music.set_volume(0.15)
    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not paused:
                        MenuScreen("Paused!", "", "Resume!", "Exit the game!").show()
                        paused = False

        if not paused:
            current_level.draw_level()
            current_level.draw_apples()
            current_level.draw_score()
            current_level.snake.update(pygame.key.get_pressed())
            current_level.snake.draw()
            pygame.display.update()

            for apple in current_level.apples:
                if current_level.snake.head.x == apple.x and current_level.snake.head.y == apple.y:
                    apple_sound.play()
                    apple_sound.set_volume(0.3)
                    apple.eat_effect()
                    apple.kill()
                    pygame.display.update()
                    current_level.draw_level()
                    current_level.draw_score()
                    current_level.spawn_apples()
                    current_level.draw_apples()

            if current_level.apples_clock >= current_level.apples_timer:
                current_level.spawn_apples()
                current_level.draw_apples()

            if current_level.score >= current_level.score_to_level_up > 0:
                current_level.level_up()
                last_score = current_level.score
                if current_level.is_final_level():
                    MenuScreen("Congratulations!", "Thanks for playing!", "Play Arcade Mode!", "Exit the game!",
                               "exit").show()
                    current_level = levels[0]
                    current_level.start(last_score)
                else:
                    MenuScreen("Good job!", "You've completed the level!", "Continue!").show()
                    current_level = current_level.next_level
                    current_level.start(last_score)

            if isinstance(current_level, ArcadeLevel):
                if current_level.map[current_level.snake.head.y][current_level.snake.head.x].cell_type == "wall" or current_level.snake.head.x == current_level.snake.tail.x and current_level.snake.head.y == current_level.snake.tail.y:
                    current_level.game_over(f"You've scored {current_level.score}", "Replay arcade!")
                    current_level.start()
                for segment in current_level.snake.segments:
                    if current_level.snake.head.x == segment.x and current_level.snake.head.y == segment.y:
                        current_level.game_over(f"You've scored {current_level.score}", "Replay arcade!")
                        current_level.start()
            else:
                if current_level.map[current_level.snake.head.y][current_level.snake.head.x].cell_type == "wall":
                    current_level.game_over("You've hit the wall!", "Replay the level")
                    current_level.start()
                for segment in current_level.snake.segments:
                    if current_level.snake.head.x == segment.x and current_level.snake.head.y == segment.y:
                        current_level.game_over("You've bitten your tail!", "Start over")
                        current_level = levels[1]
                        current_level.start()
                if current_level.snake.head.x == current_level.snake.tail.x and current_level.snake.head.y == current_level.snake.tail.y:
                    current_level.game_over("You've bitten yourself!", "Start over")
                    current_level = levels[1]
                    current_level.start()

            clock.tick(FPS)
            current_level.apples_clock += FPS
