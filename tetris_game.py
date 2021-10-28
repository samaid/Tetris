# -*- coding: utf8 -*-

import pygame
import random
import json

X_SIZE = 1200
Y_SIZE = 800

WIN_SIZE = (X_SIZE, Y_SIZE)

# Размер стакана в кубиках
JAR_N_COLS = 10
JAR_N_ROWS = 20

# Размер стенки стакана в пикселях
JAR_WALL_THICKNESS = 10

# Направление движения и вращения
DIR_LEFT = -1
DIR_RIGHT = +1
DIR_DOWN = 0
DIR_CCLOCK = -2
DIR_CLOCK = 2

# Размер элемента фигуры в пикселях
FIG_SIZE = 30

# Цвета в игре
COLOR_SCREEN = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_CYAN = (127, 127, 255)
COLOR_PURPLE = (255, 127, 127)
COLOR_YELLOW = (255, 255, 127)
COLOR_GREY = (127, 127, 127)
COLOR_JAR = (192, 192, 192)
COLOR_FIG_BORDER = (96, 96, 96)

COLOR_MAP = {'X': COLOR_SCREEN,
             'T': COLOR_RED,
             'Q': COLOR_GREEN,
             'I': COLOR_BLUE,
             'Z': COLOR_CYAN,
             'S': COLOR_PURPLE,
             'J': COLOR_YELLOW,
             'L': COLOR_GREY}

# Количество отсчетов, после которого фигура смещается вниз
MAX_TICKS = 50

# События игры
EVENT_NONE = 0
EVENT_QUIT_GAME = -1
EVENT_START_GAME = -2
EVENT_GAME_OVER = -3
EVENT_NEW_PLAYER = -4

# Классы в игре
""" 
Кодировка фигур
---------------
Фигуры кодируются с помощью последовательности нулей и единиц. 
Ноль означает, что в данной позиции нет элемента, единица - что квадратный элемент есть.
Если фигура состоит из нескольких строк, то она кодируется построчно. Сначала первая строка, затем вторая и т.д.
Конец строки кодируется цифрой 2

Рассмотрим пример фигуры T:

    ###
     #

Фигура состоит из двух строк. Кодировка этой фигуры будет: 1112010

Рассмотрим пример фигуры J:

     #
     #
    ##

Фигура состоит из трех строк. Кодировка этой фигуры будет: 01201211
"""


class Figure:
    def __init__(self, color, encoding, ftype):
        self.color = color
        self.encoding = encoding
        self.idx = 0
        self.ftype = ftype

    def draw(self, screen, x, y):
        cx = x
        cy = y
        for code in self.encoding[self.idx]:
            if code == 1:
                pygame.draw.rect(screen, self.color, (cx, cy, FIG_SIZE, FIG_SIZE))
                pygame.draw.rect(screen, COLOR_FIG_BORDER, (cx, cy, FIG_SIZE, FIG_SIZE), 1)
                cx += FIG_SIZE
            elif code == 0:
                cx += FIG_SIZE
            elif code == 2:
                cx = x
                cy += FIG_SIZE

    def rotate(self, direction):
        if direction == DIR_CCLOCK:
            # Rotate counter-clockwise
            idx = self.idx
            idx -= 1
            if idx < 0:
                idx = len(self.encoding) - 1
            self.idx = idx
        elif direction == DIR_CLOCK:
            # Rotate clockwise
            idx = self.idx
            idx += 1
            if idx >= len(self.encoding):
                idx = 0
            self.idx = idx
        else:
            raise ValueError


class FigureT(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['T'], [[1, 1, 1, 2, 0, 1],
                                          [0, 1, 2, 1, 1, 2, 0, 1],
                                          [0, 1, 2, 1, 1, 1],
                                          [1, 2, 1, 1, 2, 1]], 'T')


class FigureQ(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['Q'], [[1, 1, 2, 1, 1]], 'Q')


class FigureI(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['I'], [[1, 2, 1, 2, 1, 2, 1],
                                          [1, 1, 1, 1]], 'I')


class FigureZ(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['Z'], [[1, 1, 2, 0, 1, 1],
                                          [0, 1, 2, 1, 1, 2, 1]], 'Z')


class FigureS(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['S'], [[0, 1, 1, 2, 1, 1],
                                          [1, 2, 1, 1, 2, 0, 1]], 'S')


class FigureJ(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['J'], [[0, 1, 2, 0, 1, 2, 1, 1],
                                          [1, 2, 1, 1, 1],
                                          [1, 1, 2, 1, 2, 1]], 'J')


class FigureL(Figure):
    def __init__(self):
        super().__init__(COLOR_MAP['L'], [[1, 2, 1, 2, 1, 1],
                                          [1, 1, 1, 2, 1],
                                          [1, 1, 2, 0, 1, 2, 0, 1]], 'L')


# Сгенерировать случайную фигуру
def get_new_figure():
    return random.choice(('T', 'Q', 'I', 'Z', 'S', 'J', 'L'))


# Создать новую фигуру
def create_new_figure(ftype):
    figs = {'T': FigureT, 'Q': FigureQ, 'I': FigureI, 'Z': FigureZ, 'S': FigureS, 'J': FigureJ, 'L': FigureL}
    return figs[ftype]()


class Jar:
    def __init__(self, screen):
        self.screen = screen
        self.figure = None
        self.pos_i = 0
        self.pos_j = int(JAR_N_COLS/2-2)
        self.w = JAR_N_COLS*FIG_SIZE
        self.h = JAR_N_ROWS*FIG_SIZE
        self.xl = X_SIZE/2-self.w/2
        self.xr = X_SIZE/2+self.w/2
        self.yu = Y_SIZE/2-self.h/2
        self.yd = Y_SIZE/2+self.h/2
        self.game_field = list()
        for i in range(JAR_N_ROWS):
            row = list()
            for j in range(JAR_N_COLS):
                row.append('X')
            self.game_field.append(row)

    def x(self, j):
        return self.xl + FIG_SIZE*j

    def y(self, i):
        return self.yu + FIG_SIZE*i

    def draw(self):
        pygame.draw.rect(self.screen, COLOR_JAR, (self.xl-JAR_WALL_THICKNESS, self.yu, JAR_WALL_THICKNESS,
                                                  self.h+JAR_WALL_THICKNESS))
        pygame.draw.rect(self.screen, COLOR_JAR, (self.xr, self.yu, JAR_WALL_THICKNESS, self.h+JAR_WALL_THICKNESS))
        pygame.draw.rect(self.screen, COLOR_JAR, (self.xl-JAR_WALL_THICKNESS, self.yd, self.w+JAR_WALL_THICKNESS*2, 
                                                  JAR_WALL_THICKNESS))

        y = self.yu
        for i in range(JAR_N_ROWS):
            x = self.xl
            for j in range(JAR_N_COLS):
                sym = self.game_field[i][j]
                pygame.draw.rect(self.screen, COLOR_MAP[sym], (x, y, FIG_SIZE, FIG_SIZE))
                pygame.draw.rect(self.screen, COLOR_FIG_BORDER, (x, y, FIG_SIZE, FIG_SIZE), 1)
                x += FIG_SIZE
            y += FIG_SIZE

    def remove_full_rows(self):
        n = 0
        for i in range(JAR_N_ROWS):
            row = self.game_field[i]
            if 'X' not in set(row):
                del self.game_field[i]
                row = list()
                for j in range(JAR_N_COLS):
                    row.append('X')
                self.game_field.insert(0, row)
                n += 1
        return n

    def fill_game_field(self):
        i = self.pos_i
        j = self.pos_j
        for code in self.figure.encoding[self.figure.idx]:
            if code == 1:
                self.game_field[i][j] = self.figure.ftype
                j += 1
            elif code == 0:
                j += 1
            elif code == 2:
                j = self.pos_j
                i += 1

    def clear_game_field(self):
        i = self.pos_i
        j = self.pos_j
        for code in self.figure.encoding[self.figure.idx]:
            if code == 1:
                self.game_field[i][j] = 'X'
                j += 1
            elif code == 0:
                j += 1
            elif code == 2:
                j = self.pos_j
                i += 1

    def new_figure(self, f):
        self.figure = f
        self.pos_j = int(JAR_N_COLS/2-2)
        self.pos_i = 0
        self.fill_game_field()

    def can_move(self, direction):
        pos_i = self.pos_i
        pos_j = self.pos_j
        idx = self.figure.idx
        can = True
        if direction == DIR_LEFT:
            # Move left
            pos_j -= 1
            if pos_j < 0:
                can = False
        elif direction == DIR_RIGHT:
            # Move right
            pos_j += 1
        elif direction == DIR_DOWN:
            # Move down
            pos_i += 1
        elif direction == DIR_CCLOCK:
            # Rotate counter-clockwise
            self.figure.rotate(DIR_CCLOCK)
        elif direction == DIR_CLOCK:
            # Rotate clockwise
            self.figure.rotate(DIR_CLOCK)
        else:
            raise ValueError

        i = pos_i
        j = pos_j

        for code in self.figure.encoding[self.figure.idx]:
            if code == 1:
                if j >= JAR_N_COLS:
                    can = False
                    break
                if i >= JAR_N_ROWS:
                    can = False
                    break
                if self.game_field[i][j] != 'X':
                    can = False
                    break
                j += 1
            elif code == 0:
                j += 1
            elif code == 2:
                j = pos_j
                i += 1
        self.figure.idx = idx
        return can

    def move(self, direction):
        self.clear_game_field()
        can_move = self.can_move(direction)
        if direction == DIR_LEFT:
            # Move left
            if can_move:
                self.pos_j -= 1
        elif direction == DIR_RIGHT:
            # Move right
            if can_move:
                self.pos_j += 1
        elif direction == DIR_DOWN:
            # Move down
            if can_move:
                self.pos_i += 1
        elif direction == DIR_CCLOCK or direction == DIR_CLOCK:
            # Rotate counter-clockwise
            if can_move:
                self.figure.rotate(direction)
        else:
            raise ValueError
        self.fill_game_field()
        return can_move


class Players:
    def __init__(self):
        self.players = [{"Name": "Player1", "Score": 0},
                        {"Name": "Player2", "Score": 0},
                        {"Name": "Player3", "Score": 0},
                        {"Name": "Player4", "Score": 0},
                        {"Name": "Player5", "Score": 0},
                        {"Name": "NEW PLAYER", "Score": 0}]
        self.render_all_player_surfaces()

    def render_player_surface(self, idx):
        player_font = pygame.font.SysFont('Courier New', 30)
        s = '{:2d}{:>20}{:10d}'.format(idx + 1, self.players[idx]["Name"], self.players[idx]["Score"])
        surface = player_font.render(s, False, COLOR_CYAN)
        return surface

    def render_all_player_surfaces(self):
        self.player_surfaces = list()
        for i in range(len(self.players)):
            surface = self.render_player_surface(i)
            self.player_surfaces.append(surface)

    def __getitem__(self, idx):
        return self.players[idx]

    def __setitem__(self, idx, value):
        self.players[idx] = value
        surface = self.render_player_surface(idx)
        self.player_surfaces[idx] = surface

    def __len__(self):
        return len(self.players)

    def sort(self):
        self.players.sort(key=lambda x: x['Score'], reverse=True)
        self.render_all_player_surfaces()

    def draw(self, screen, x, y, highlight_player):
        cx = x
        cy = y
        for surface in self.player_surfaces:
            screen.blit(surface, (cx, cy))
            cy += 40

        if 0 <= highlight_player < len(self.players):
            cy = y + highlight_player * 40 - 5
            pygame.draw.rect(screen, COLOR_CYAN, (cx - 5, cy, 600, 40), 2)

    def load(self):
        with open('records.dat') as f:
            top_players = json.load(f)
        self.players = top_players
        self.players.append({"Name": "NEW PLAYER", "Score": 0})
        self.render_all_player_surfaces()

    def save(self):
        top_players = self.players[:-1]
        with open('records.dat', 'w') as f:
            json.dump(top_players, f)


def do_select_player(screen, players):
    return_event = EVENT_NONE
    selected_player = 0
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Comic Sans MS', 40)
    enter_name_surface = font.render('SELECT PLAYER', False, COLOR_YELLOW)

    while return_event == EVENT_NONE:
        # Оброботка событей
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_event = EVENT_QUIT_GAME
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_player == len(players) - 1:
                        player = players[selected_player]
                        player["Name"] = ''
                        players[selected_player] = player
                        return_event = EVENT_NEW_PLAYER
                    else:
                        return_event = EVENT_START_GAME
                if event.key == pygame.K_DOWN:
                    if selected_player < len(players)-1:
                        selected_player += 1
                if event.key == pygame.K_UP:
                    if selected_player > 0:
                        selected_player -= 1

        # Перерисовка
        screen.fill(COLOR_SCREEN)
        screen.blit(enter_name_surface, (X_SIZE / 2 - 130, 100))
        players.draw(screen, X_SIZE / 2 - 250, 180, selected_player)

        # Каждая итерация заканчивается этими двумя командами
        pygame.display.flip()  # Отображаем перерисованное на экране
        clock.tick(60)  # Каждая итерация занимает 60 миллисекунд

    return return_event, selected_player


def do_enter_new_player(screen, players):
    return_event = EVENT_NONE
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Comic Sans MS', 40)
    enter_name_surface = font.render('SELECT PLAYER', False, COLOR_YELLOW)

    while return_event == EVENT_NONE:
        # Оброботка событей
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_event = EVENT_QUIT_GAME
            elif event.type == pygame.KEYDOWN:
                if pygame.K_a <= event.key <= pygame.K_z:
                    player = players[len(players)-1]
                    if len(player["Name"]) < 15:
                        player["Name"] += chr(event.key)
                    players[len(players)-1] = player
                elif event.key == pygame.K_RETURN:
                    return_event = EVENT_START_GAME

        # Перерисовка
        screen.fill(COLOR_SCREEN)
        screen.blit(enter_name_surface, (X_SIZE / 2 - 130, 100))
        players.draw(screen, X_SIZE / 2 - 250, 180, len(players)-1)

        # Каждая итерация заканчивается этими двумя командами
        pygame.display.flip()  # Отображаем перерисованное на экране
        clock.tick(60)  # Каждая итерация занимает 60 миллисекунд

    return return_event


def do_game(screen, player_name):
    return_event = EVENT_NONE
    clock = pygame.time.Clock()
    random.seed(a=None)
    score = 0

    # Надписи в игре
    font = pygame.font.SysFont('Comic Sans MS', 30)
    enter_surface = font.render('Enter - Begin game', False, COLOR_JAR)
    space_surface = font.render('Space - Drop figure', False, COLOR_JAR)
    left_surface = font.render('Left - Move figure left', False, COLOR_JAR)
    right_surface = font.render('Right - Move figure right', False, COLOR_JAR)
    up_surface = font.render('Up - Rotate counter-clockwise', False, COLOR_JAR)
    down_surface = font.render('Down - Rotate clockwise', False, COLOR_JAR)

    need_new_figure = True
    ftype = get_new_figure()
    next_figure = create_new_figure(ftype)

    ticks = 0  # Количество отсчетов. По истечению MAX_TICKS фигура смещается вниз
    jar = Jar(screen)

    while return_event == EVENT_NONE:
        # Оброботка событей
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_event = EVENT_QUIT_GAME
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    jar.move(DIR_LEFT)
                if event.key == pygame.K_RIGHT:
                    jar.move(DIR_RIGHT)
                if event.key == pygame.K_UP:
                    jar.move(DIR_CCLOCK)
                if event.key == pygame.K_DOWN:
                    jar.move(DIR_CLOCK)
                if event.key == pygame.K_SPACE:
                    while jar.move(DIR_DOWN):
                        pass

        # Логика игры
        if need_new_figure:
            jar.new_figure(next_figure)
            ftype = get_new_figure()
            next_figure = create_new_figure(ftype)
            need_new_figure = False
            ticks = 0

        has_moved = True
        if ticks >= MAX_TICKS:
            has_moved = jar.move(DIR_DOWN)
            ticks = 0

        if not has_moved:
            if jar.pos_i == 0:
                return_event = EVENT_GAME_OVER
            else:
                need_new_figure = True
                removed_rows = jar.remove_full_rows()
                score += removed_rows

        ticks += 1

        # Перерисовка
        screen.fill(COLOR_SCREEN)
        screen.blit(enter_surface, (10, 10))
        screen.blit(space_surface, (10, 40))
        screen.blit(left_surface, (10, 70))
        screen.blit(right_surface, (10, 110))
        screen.blit(up_surface, (10, 150))
        screen.blit(down_surface, (10, 190))

        jar.draw()
        next_figure.draw(screen, (jar.xr + X_SIZE) / 2 - 2 * FIG_SIZE, 100)

        # Каждая итерация заканчивается этими двумя командами
        pygame.display.flip()  # Отображаем перерисованное на экране
        clock.tick(60)  # Каждая итерация занимает 60 миллисекунд

    return return_event, score


def do_game_over(screen, players):
    return_event = EVENT_NONE
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('Comic Sans MS', 40)
    game_over_surface = font.render('GAME OVER', False, COLOR_YELLOW)
    continue_surface = font.render('Continue? Y/N', False, COLOR_YELLOW)
    font = pygame.font.SysFont('Comic Sans MS', 30)
    best_players_surface = font.render('Best players', False, COLOR_CYAN)

    players.sort()

    while return_event == EVENT_NONE:
        # Оброботка событей
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_event = EVENT_QUIT_GAME
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return_event = EVENT_START_GAME
                if event.key == pygame.K_n:
                    return_event = EVENT_QUIT_GAME

        # Перерисовка
        screen.fill(COLOR_SCREEN)
        screen.blit(game_over_surface, (X_SIZE / 2 - 100, 100))
        screen.blit(continue_surface, (X_SIZE / 2 - 110, 500))
        screen.blit(best_players_surface, (X_SIZE / 2 - 60, 200))
        players.draw(screen, X_SIZE / 2 - 250, 250, -1)

        # Каждая итерация заканчивается этими двумя командами
        pygame.display.flip()  # Отображаем перерисованное на экране
        clock.tick(60)  # Каждая итерация занимает 60 миллисекунд

    return return_event


def main():
    # Программа должна начинаться с инициализации pygame

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Tetris")

    # Выбор игрока
    players = Players()
    players.load()

    event, player_idx = do_select_player(screen, players)

    if event == EVENT_NEW_PLAYER:
        event = do_enter_new_player(screen, players)

    while event == EVENT_START_GAME:
        event, score = do_game(screen, players[player_idx]["Name"])
        best_score = players[player_idx]["Score"]
        if score > best_score:
            players[player_idx]["Score"] = score

        if event == EVENT_GAME_OVER:
            event = do_game_over(screen, players)

    players.save()
    # Освобождаем память по окончании игры
    pygame.quit()


if __name__ == "__main__":
    main()
