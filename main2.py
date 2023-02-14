import random


class CharStyle:

    empty = 'e'
    fog = 'O'
    desk = chr(9632)
    hit = 'X'
    miss = 'T'
    buffer = 'b'
    splitter = '|'


class Desk:
    def __init__(self, x, y, alive=True):
        self.x = x
        self.y = y
        self.alive = alive


class Ship:
    def __init__(self, desk_list: list):
        self.desks = []
        self.lenght = len(desk_list)
        self.alive = True
        for item in desk_list:
            self.desks.append(Desk(x=item[0], y=item[1]))

    def __repr__(self):
        return f'Ship: lenght:{self.lenght}, alive:{self.alive}, desks:{self.desks}'

    def hit(self, x, y):
        for desk in self.desks:
            if x == desk.x and y == desk.y:
                desk.alive = False
                return True
        return False

    def check_alive(self):
        alive = False
        for desk in self.desks:
            alive = desk.alive or alive
        self.alive = alive
        return self.alive


class Board:
    def __init__(self, shiplen_list: list, dim, name, hide_alive=True):
        self.name = name
        self.dim = dim
        self.notSpawned = list(shiplen_list)
        self.ships = []
        self.cells = []
        self.fog = []
        self.choices = []
        self.clear_board()
        self.hide_alive = hide_alive

    def clear_board(self):
        self.cells = []
        self.fog = []
        for i in range(self.dim):
            fog_row = [CharStyle.fog] * self.dim
            cell_row = [CharStyle.empty] * self.dim
            self.cells.append(cell_row)
            self.fog.append(fog_row)
        for ship in self.ships:
            self.notSpawned.append(ship.lenght)
        self.ships = []
        self.reset_choices()

    def reset_choices(self):
        self.choices = []
        for x in range(self.dim):
            for y in range(self.dim):
                self.choices.append((x, y))

    def spawn(self):
        counter = 0
        while len(self.notSpawned) > 0:
            counter += 1
            if counter > self.dim * self.dim * 2:  # restart if can't place ship
                self.clear_board()
                counter = 0
            shiplen = max(self.notSpawned)
            pos_x, pos_y = random.choice(self.choices)

            rotation = random.choice([True, False])
            dx = rotation
            dy = not rotation
            if self.can_place(pos_x, pos_y, rotation, shiplen):
                desk_list = []
                for i in range(shiplen):
                    x = pos_x + dx * i
                    y = pos_y + dy * i
                    self.choices.remove((x, y))
                    desk_list.append((x, y))
                    self.cells[y][x] = CharStyle.desk
                cur_ship = Ship(desk_list)
                self.ships.append(cur_ship)
                self.add_buffer(cur_ship)
                self.notSpawned.remove(shiplen)
        self.reset_choices()
        self.update_fog()

    def can_place(self, x, y, rotation, lenght):
        dx = rotation
        dy = not rotation
        if x + dx * lenght > self.dim or y + dy * lenght > self.dim:
            return False
        for i in range(lenght):
            if self.cells[y + dy * i][x + dx * i] != CharStyle.empty:
                return False
        return True

    def add_buffer(self, ship: Ship):
        for desk in ship.desks:
            for dx in range(-1, 2):
                x = desk.x + dx
                if x not in range(self.dim):
                    continue
                for dy in range(-1, 2):
                    y = desk.y + dy
                    if y not in range(self.dim):
                        continue
                    if self.cells[y][x] == CharStyle.empty:
                        self.cells[y][x] = CharStyle.buffer

    def update_fog(self):
        for ship in self.ships:
            for desk in ship.desks:
                if not desk.alive:
                    self.fog[desk.y][desk.x] = CharStyle.hit
                elif not self.hide_alive:
                    self.fog[desk.y][desk.x] = CharStyle.desk

    def out(self):
        print(f'\n{self.name}:')
        row0 = ' ' + CharStyle.splitter
        for i in range(self.dim):
            row0 += str(i + 1) + CharStyle.splitter
        print(row0)
        for i, row in enumerate(self.fog):
            out = str(i + 1) + CharStyle.splitter
            for value in row:
                out += value + CharStyle.splitter
            print(out)

    def hit(self, x, y):
        result = False
        for ship in self.ships:
            result = ship.hit(x, y) or result
        if result:
            self.fog[y][x] = CharStyle.hit
        else:
            self.fog[y][x] = CharStyle.miss
        self.choices.remove((x, y))
        return result

    def ships_alive(self):
        count = 0
        for ship in self.ships:
            count += ship.check_alive()
        return count


def input_coord(text: str):
    flag = True
    while flag:
        try:
            coord = int(input(text))
            if not (1 <= coord <= 6):
                raise ValueError
        except ValueError:
            print('Нужно вводить целые числа от 1 до 6')
            continue
        flag = False
    return coord-1


if __name__ == '__main__':
    dim = 6
    ship_list = (4, 2, 2, 1, 1, 1, 1)
    player = Board(ship_list, dim, name='Игрок', hide_alive=False)
    player.spawn()
    enemy = Board(ship_list, dim, name='Компьютер', hide_alive=False)
    enemy.spawn()
    gameOver = False

    while not gameOver:
        enemy.out()
        player.out()
        flag = True
        while flag:
            x = input_coord('\nВведите координату x: ')
            y = input_coord('Введите координату y: ')
            if (x, y) not in enemy.choices:
                print('Вы сюда уже стреляли')
                continue
            else:
                flag = False
        hit = enemy.hit(x, y)
        if hit:
            print('Поздравляем, вы попали')
        else:
            print('Промах!')
        if enemy.ships_alive() < 1:
            enemy.out()
            print('\nПоздравляем, вы победили!!!')
            gameOver = True
            break
        x, y = random.choice(player.choices)
        print(f'Враг стреляет на {x+1}, {y+1}. ', end='')
        hit = player.hit(x, y)
        if hit:
            print('Попадание!')
        else:
            print('Промах!')
        if player.ships_alive() < 1:
            player.out()
            print('\nВы проиграли!!!')
            gameOver = True
            break

