#!/usr/bin/env python3
from random import randint
from os import system, name
maps = {}

class Ship:
    def __init__(self, map_id: int, size: int, coordinates: tuple):
        self.map_id = map_id
        self.size = size
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.fields = []
        self.durability = size
        self.status = "alive"

    def is_dead(self, field: str):
        if field in self.fields and self.status == "alive":
            self.durability -= 1
            if self.durability == 0:
                self.status = "dead"
                return True

class Map:
    def __init__(self, map_id: int):
        self.map = {"A": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "B": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "C": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "D": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "E": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "F": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "G": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "H": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "I": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
                    "J": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]}
        self.id = map_id

    def check_field(self, field: tuple):
        x = field[0].upper()
        y = int(field[1])
        if self.map[x][y] == "-":
            return True
        else:
            return False

    def change_field(self, field: tuple, symbol: str, pass_check=False):
        x = field[0].upper()
        y = int(field[1]) - 1
        if self.check_field((x, y)) or pass_check is True:
            self.map[x][y] = symbol
            return True
        else:
            return False

    def place_collision(self, ship: Ship, symbol: str):
        fields_list = []
        keys = list(self.map.keys())
        if ship.x[0] == ship.y[0]:
            try:
                fields_list.append((ship.x[0], int(ship.x[1:])-1))
                fields_list.append((ship.y[0], int(ship.y[1:])+1))
            except IndexError:
                pass
            for i in range(int(ship.x[1:])-1, int(ship.y[1:])+2):
                try:
                    if keys.index(ship.x[0].upper()) - 1 >= 0:
                        fields_list.append((keys[keys.index(ship.x[0].upper()) - 1], i))
                    fields_list.append((keys[keys.index(ship.x[0].upper()) + 1], i))
                except IndexError:
                    pass
        else:
            try:
                if keys.index(ship.x[0].upper()) - 1 >= 0:
                    fields_list.append((keys[keys.index(ship.x[0].upper()) - 1], int(ship.x[1:])))
                fields_list.append((keys[keys.index(ship.y[0].upper()) + 1], int(ship.x[1:])))
            except IndexError:
                pass
            for i in range(keys.index(ship.x[0].upper())-1, keys.index(ship.y[0].upper())+2):
                try:
                    if i >= 0:
                        fields_list.append((keys[i], int(ship.x[1:]) - 1))
                        fields_list.append((keys[i], int(ship.x[1:]) + 1))
                except IndexError:
                    break

        for coordinates in fields_list:
            if 0 < int(coordinates[1]) <= 10:
                self.change_field(coordinates, symbol)

class ShipSpacingMap(Map):
    def __init__(self, map_id):
        super().__init__(map_id)
        self.ships = []

    def place_ship(self, ship: Ship):
        validate = []
        if ship.x[0] == ship.y[0]:
            if int(ship.y[1:]) - int(ship.x[1:]) + 1 == ship.size:
                for i in range(int(ship.x[1:]), int(ship.y[1:]) + 1):
                    ship.fields.append(f"{ship.x[0]}{i}")
                    validate.append(super().change_field((ship.x[0], i), "s"))
                    if False not in validate and i == int(ship.y[1:]):
                        self.place_collision(ship, "*")
                        self.ships.append(ship)
                        return True
        elif ship.x[1:] == ship.y[1:]:
            keys = list(self.map.keys())
            if keys.index(ship.y[0].upper()) + 1 - keys.index(ship.x[0].upper()) == ship.size:
                for i in range(keys.index(ship.x[0].upper()), keys.index(ship.y[0].upper()) + 1):
                    ship.fields.append(f"{keys[i]}{ship.y[1:]}")
                    validate.append(super().change_field((keys[i], int(ship.y[1:])), "s"))
                    if False not in validate and i == keys.index(ship.y[0].upper()):
                        self.place_collision(ship, "*")
                        self.ships.append(ship)
                        return True
        else:
            return 1

    def del_collision(self):
        for letter in self.map.keys():
            for i in range(0, len(self.map)):
                if self.map[letter][i] == "*":
                    self.map[letter][i] = "-"

    def repair_map(self):
        ships_fields = []
        for ship in self.ships:
            ships_fields.extend(ship.fields)
        for letter in self.map.keys():
            for i in range(0, len(self.map)):
                if self.map[letter][i] == "s" and f"{letter}{i+1}" not in ships_fields:
                    self.map[letter][i] = "-"

class ShotMap(Map):
    def __init__(self, map_id):
        super().__init__(map_id)
        self.opponent_map = maps[-map_id]

    def shoot(self, coordinates: str):
        x = coordinates[0].upper()
        y = coordinates[1:]
        if self.check_field((x, int(y) - 1)):
            if self.opponent_map.check_field((x, int(y) - 1)):
                self.change_field((x, y), "o")
                self.opponent_map.change_field((x, y), "o", pass_check=True)
                return False
            else:
                self.change_field((x, y), "x")
                self.opponent_map.change_field((x, y), "x", pass_check=True)
                self.check_ship(f"{x}{y}")
                return True
        else:
            return False

    def check_ship(self, field: str):
        for ship in self.opponent_map.ships:
            if ship.is_dead(field):
                self.place_collision(ship, "o")
                break

class Game:
    def __init__(self, difficulty: int = 0, map_auto: int = 0):
        self.state = "main_menu"
        self.ship_list = {"5": 1, "4": 2, "3": 2, "2": 2}
        self.letter_to_number = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10}
        self.order = []
        self.ai_difficulty = difficulty
        self.player_map_auto = map_auto

    def main_menu(self):
        print("BITWA MORSKA\n"
              "1 - Gra z komputerem\n"
              "2 - Gra z innym graczem (wkrótce)\n"
              "3 - Instrukcja\n")
        while True:
            decision = input("> ")
            if decision == "1":
                while True:
                    self.ai_difficulty = int(input("Wybierz poziom trudności:\n"
                                                   "1 - Łatwy\n"
                                                   "2 - Średni\n"
                                                   "3 - Trudny\n"
                                                   "> ")) - 1
                    if self.ai_difficulty in range(3):
                        break
                while True:
                    self.player_map_auto = int(input("Jak chcesz rozstawić statki?\n"
                                                     "1 - Manualnie\n"
                                                     "2 - Automatycznie\n"
                                                     "> ")) - 1
                    if self.player_map_auto in range(2):
                        break
                session = Game(self.ai_difficulty, self.player_map_auto)
                session.preparing(0)
            elif decision == "2":
                session = Game(self.ai_difficulty, self.player_map_auto)
                session.preparing(1)
            elif decision == "3":
                self.instruction()
            else:
                print("Nieprawidłowa wartość!")

    def instruction(self):
        print("INSTRUKCJA\n")
        while True:
            decision = input("> ")
            if decision == "exit":
                self.main_menu()
            else:
                print("Nieprawidłowa wartość!")

    def ai(self, ai_ship_map: ShipSpacingMap):
        if self.state == "preparing":
            for ship in self.ship_list:
                i = 0
                while i != self.ship_list[ship]:
                    coordinates = f"{list(self.letter_to_number.keys())[randint(0, 9)]}{randint(1, 10)} " \
                                  f"{list(self.letter_to_number.keys())[randint(0, 9)]}{randint(1, 10)}"
                    coordinates = coordinates.split()
                    if coordinates[0][0] == coordinates[1][0]:
                        size = int(coordinates[1][1:]) - int(coordinates[0][1:]) + 1
                    else:
                        size = self.letter_to_number[coordinates[1][0].upper()] - \
                               self.letter_to_number[coordinates[0][0].upper()] + 1
                    if size == int(ship):
                        if ai_ship_map.place_ship(ship=Ship(-1, int(ship), (coordinates[0], coordinates[1]))) is True:
                            i += 1
        else:
            if self.ai_difficulty == 0:
                while True:
                    coordinates = f"{list(self.letter_to_number.keys())[randint(0, 9)]}{randint(1, 10)}"
                    if not maps[-1].shoot(coordinates):
                        break
            elif self.ai_difficulty == 1:
                pass
            else:
                pass

    def player_turn(self, player_ship_map: ShipSpacingMap):
        if self.state == "preparing":
            for ship in self.ship_list:
                i = 0
                while i != self.ship_list[ship]:
                    self.render("ship_map")
                    coordinates = input(f"Podaj współrzędne dla {ship}-masztowca: \n"
                                        "> ")
                    coordinates = coordinates.split()
                    if coordinates[0][0] == coordinates[1][0]:
                        size = int(coordinates[1][1:]) - int(coordinates[0][1:]) + 1
                    else:
                        size = self.letter_to_number[coordinates[1][0].upper()] - \
                               self.letter_to_number[coordinates[0][0].upper()] + 1
                    if size == int(ship):
                        if player_ship_map.place_ship(ship=Ship(1, int(ship), (coordinates[0], coordinates[1])))\
                                is True:
                            i += 1
                        elif player_ship_map.place_ship(ship=Ship(1, int(ship), (coordinates[0], coordinates[1]))) == 1:
                            print("Błędne współrzędne!")
                        else:
                            print("Nie możesz tu umieścić okrętu, kolizja z innym okrętem!")
                    else:
                        print(f"Nieprawidłowy rozmiar okrętu! Podany rozmiar to {size}, "
                              f"natomiast wymagany jest {ship}!")
            self.state = "playing"
        else:
            while True:
                coordinates = input("Podaj współrzędne do strzału: \n"
                                    "> ")
                if not maps[2].shoot(coordinates):
                    break
                else:
                    self.render()

    @staticmethod
    def is_victory():
        j = 0
        map_id = 1
        player_1 = False
        player_2 = False
        while j != 2:
            for letter in maps[map_id].map.keys():
                for i in range(0, len(maps[map_id].map)):
                    if maps[map_id].map[letter][i] == "s":
                        if map_id == 1:
                            player_1 = True
                        else:
                            player_2 = True
            j += 1
            map_id -= 3

        if player_1 is True and player_2 is True:
            return False
        elif player_1 is False:
            return True, "player_2"
        elif player_2 is False:
            return True, "player_1"

    def preparing(self, mode: int):
        self.state = "preparing"
        maps[1] = ShipSpacingMap(1)     # Player1 ship map
        maps[-2] = ShipSpacingMap(-2)   # Player2 ship map
        maps[2] = ShotMap(2)            # Player1 shot map
        maps[-1] = ShotMap(-1)          # Player2 shot map
        if mode == 0:
            self.ai(maps[-2])
            maps[-2].del_collision()
            maps[-2].repair_map()
            if self.player_map_auto == 0:
                self.player_turn(maps[1])
                maps[1].del_collision()
            else:
                self.ai(maps[1])
                maps[1].del_collision()
                maps[1].repair_map()
                self.state = "playing"
            if randint(0, 1) == 0:
                self.order = ["player_1", "player_2"]
            else:
                self.order = ["player_2", "player_1"]
            self.main_loop(0)

    @staticmethod
    def render(render="all"):
        shot_map = "  1 2 3 4 5 6 7 8 9 10\n"
        ship_map = "  1 2 3 4 5 6 7 8 9 10\n"
        if name == "nt":
            system("cls")
        else:
            system("clear")

        if render == "all":
            for letter, fields in maps[2].map.items():
                shot_map += letter + " "
                for i, field in enumerate(fields):
                    if i % 9 == 0 and i != 0:
                        shot_map += field + " \n"
                    else:
                        shot_map += field + " "
            for letter, fields in maps[1].map.items():
                ship_map += letter + " "
                for i, field in enumerate(fields):
                    if i % 9 == 0 and i != 0:
                        ship_map += field + " \n"
                    else:
                        ship_map += field + " "
            print(f"{shot_map}{ship_map}")
        else:
            for letter, fields in maps[1].map.items():
                ship_map += letter + " "
                for i, field in enumerate(fields):
                    if i % 9 == 0 and i != 0:
                        ship_map += field + " \n"
                    else:
                        ship_map += field + " "
            print(ship_map)

    def main_loop(self, mode: int):
        if mode == 0:
            while True:
                if self.is_victory():
                    print(f"Wygrał {self.is_victory()[1]}")
                    break
                order = self.order.pop(0)
                self.order.append(order)
                if order == "player_1":
                    self.render()
                    self.player_turn(maps[1])
                else:
                    self.ai(maps[-2])
            self.main_menu()
        else:
            pass

if __name__ == "__main__":
    game = Game()
    game.main_menu()
