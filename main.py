import os
import sys
from typing import List, Tuple

import pygame
from pygame.time import Clock

FPS = 60

directions = {
    81: (0, 1),
    82: (0, -1),
    80: (-1, 0),
    79: (1, 0),
    26: (0, -1),
    22: (0, 1),
    4: (-1, 0),
    7: (1, 0),
}


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    board = Board()
    for y in range(len(level)):
        tiles = []
        for x in range(len(level[y])):
            if level[y][x] == '.':
                tiles.append(Tile('empty', x, y))
            elif level[y][x] == '#':
                tiles.append(Tile('wall', x, y))
            elif level[y][x] == '@':
                tiles.append(Tile('empty', x, y))
                new_player = Player(x, y)
        board.append(tiles)
    # вернем игрока, а также размер поле
    return new_player, board


def terminate():
    pygame.quit()
    sys.exit()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Board:
    def __init__(self):
        self.tiles: List[List[Tile]] = []
        self.player_pos = (0, 0)

        self.x, self.y = None, None

    def append(self, tile: List[Tile]):
        self.tiles.append(tile)
        self.x = len(self.tiles[0])
        self.y = len(self.tiles)

    def set_player_pos(self, pos: Tuple[int, int]):
        self.player_pos = pos

    def size(self):
        return self.x, self.y

    def __getitem__(self, item):
        return self.tiles[item]


# class Camera:
#     # зададим начальный сдвиг камеры
#     def __init__(self):
#         self.dx = 0
#         self.dy = 0
#
#     # сдвинуть объект obj на смещение камеры
#     def apply(self, obj):
#         obj.rect.x += self.dx
#         obj.rect.y += self.dy
#
#     # позиционировать камеру на объекте target
#     def update(self, target):
#         self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
#         self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = [pos_x, pos_y]

    def move(self, scancode: int):
        direction = directions.get(scancode, 0)
        if not direction:
            return
        pos = self.pos[0] + direction[0], self.pos[1] + direction[1]
        if board[pos[1]][pos[0]].image == tile_images['wall']:
            return

        self.pos = pos
        self.rect = self.image.get_rect().move(tile_width * pos[0] + 15, tile_height * pos[1] + 5)


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = load_image('fon.jpg')
    fon = pygame.transform.scale(fon, (fon.get_width(), fon.get_height()))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Перемещение героя')

    fps = 60

    tile_width = tile_height = 50

    level = load_level('map.txt')

    size = WIDTH, HEIGHT = tile_width * len(level[0]), tile_height * len(level)
    screen = pygame.display.set_mode(size)

    # основной персонаж
    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mario.png')

    player, board = generate_level(level)
    player_x, player_y = player.pos

    level_x, level_y = board.size()

    # camera = Camera()

    clock = Clock()
    running = True

    start_screen()

    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                player.move(event.scancode)

        # изменяем ракурс камеры
        #  camera.update(player)
        #  # обновляем положение всех спрайтов
        #  for sprite in all_sprites:
        #      camera.apply(sprite)

        all_sprites.draw(screen)
        all_sprites.update()
        player_group.draw(screen)
        pygame.display.flip()

        clock.tick(fps)

    pygame.quit()
