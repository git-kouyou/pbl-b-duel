import typing
from boarddata import BoardData, Type
from collections import deque
from enum import Enum

X = 0
Y = 1

class Status(Enum):
    loop = 0
    eat_food = 1

class EnemySnakeData:
    def __init__(self, enemy_snake_data):
        # 体の座標(tuple)一覧
        self.bodies = enemy_snake_data["body"]
        # 体の座標(tuple)一覧
        self.bodies = deque()
        seen = set()
        for body in enemy_snake_data["body"]:
            pos = (body["x"], body["y"])
            if pos not in seen:
                seen.add(pos)
                self.bodies.append(pos)

    # 頭の座標
    def head(self):
        return self.bodies[0]
    
    # 首の座標
    def neck(self):
        return self.bodies[1] if len(self.bodies) > 1  else self.head()
    
    # 尾の座標
    def tail(self):
        return self.bodies[-1]
    
    # 体の長さ
    def length(self):
        return len(self.bodies)
    
    # 頭回り
    def head_around(self):
        result = set()
        result.add((self.head()[X] + 1, self.head()[Y]))
        result.add((self.head()[X] - 1, self.head()[Y]))
        result.add((self.head()[X], self.head()[Y] + 1))
        result.add((self.head()[X], self.head()[Y] - 1))
        return result

class MySnakeData:
    previous_foods:typing.Set[typing.Tuple[int, int]]
    status: Status = Status.loop
    disignated_route: deque
    isDisignated: bool
    initialized = False

    def __init__(self, board_data: BoardData, my_snake_data, enemy_snake_data: EnemySnakeData, bodies = list(), foods = []):
        if my_snake_data == {} and bodies == []:
            print("cannot initialize GameData!")
            exit(1)

        # 初生成時にクラス変数を初期化
        if not MySnakeData.initialized:
            # GameData.previous_foods = set((food["x"], food["y"]) for food in game_state["board"]["food"])
            MySnakeData.status = Status.loop
            #初期化済み
            MySnakeData.initialized = True
            print(f"Snake:{my_snake_data['name']}Data initialized")


        # 盤面情報
        self.board = board_data.board
        # 体の座標(tuple)一覧
        self.bodies = deque()
        if not bodies:
            seen = set()
            for body in my_snake_data["body"]:
                pos = (body["x"], body["y"])
                if pos not in seen:
                    seen.add(pos)
                    self.bodies.append(pos)
        else:
            self.bodies = bodies
        # 残り体力
        self.health = my_snake_data["health"]

        # 敵の情報
        self.enemy_snake_data = enemy_snake_data

    # 餌を食べた直後ならばTrueを返す
    # def ate_food(self):
    #     return self.previous_foods != self.foods

    # 頭の座標
    def head(self):
        return self.bodies[0]
    
    # 首の座標
    def neck(self):
        return self.bodies[1] if len(self.bodies) > 1  else self.head()
    
    # 尾の座標
    def tail(self):
        return self.bodies[-1]
    
    # 体の長さ
    def length(self):
        return len(self.bodies)
    
    # 周りの進行可能方向のリスト
    def empty_around(self) -> set[str]:
        result = set()
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] <= Type.safe.value:
            result.add("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] <= Type.safe.value:
            result.add("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] <= Type.safe.value:
            result.add("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] <= Type.safe.value:
            result.add("down")
        return result
    
    # 進行不可能方向(潜在的な詰み含む)のリスト
    def unsafes_around(self) -> set[str]:
        result = set()
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] >= Type.body.value + 1:
            result.add("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] >= Type.body.value + 1:
            result.add("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] >= Type.body.value + 1:
            result.add("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] >= Type.body.value + 1:
            result.add("down")
        
        if (head[X] + 1, head[Y]) in self.enemy_snake_data.head_around():
            result.add("right")
        if (head[X] , head[Y] + 1) in self.enemy_snake_data.head_around():
            result.add("up")
        if (head[X] - 1, head[Y]) in self.enemy_snake_data.head_around():
            result.add("left")
        if (head[X], head[Y] - 1) in self.enemy_snake_data.head_around():
            result.add("down")

        return result
    
    # 周りの餌のある方向のリスト
    def foods_around(self) -> set[str]:
        result = set()
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] == Type.food.value:
            result.add("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] == Type.food.value:
            result.add("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] == Type.food.value:
            result.add("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] == Type.food.value:
            result.add("down")
        return result
    
    # 周りの安全な方向のリスト
    def safes_around(self) -> set[str]:
        return set(["right", "up", "left", "down"]) - self.unsafes_around()
    
    # 餌のない安全な方向のリスト
    def no_foods(self) -> set[str]:
            return self.safes_around() - self.foods_around()
        
    # 現在の進行方向
    def heading(self):
        head = self.head()
        neck = self.neck()
        if head[X] < neck[X]:
            return "left"
        elif head[X] > neck[X]:
            return "right"
        elif head[Y] < neck[Y]:
            return "down"
        else:
            return "up"
        
    #進む方向によって次の頭の位置を返す
    def next_head_position(self, head: typing.Tuple[int, int], move: str) -> typing.Tuple[int, int]:
        if move == "right":
            return (head[X] + 1, head[Y])
        elif move == "up":
            return (head[X], head[Y] + 1)
        elif move == "left":
            return (head[X] - 1, head[Y])
        else:
            return (head[X], head[Y] - 1)
        
    def enemy_head_around(self, enemy_snake_data: typing.Self) -> set[str]:
        result = set()
        if enemy_snake_data.length() < self.length():
            enemy_head_neighbors = [enemy_snake_data.next_head_position(enemy_snake_data.head(), move) for move in enemy_snake_data.empty_around()]
            
            if self.next_head_position(self.head(), "right") in enemy_head_neighbors and self.next_head_position(self.head(), "right") not in self.bodies:
                result.add("right")
            if self.next_head_position(self.head(), "up") in enemy_head_neighbors and self.next_head_position(self.head(), "up") not in self.bodies:
                result.add("up")
            if self.next_head_position(self.head(), "left") in enemy_head_neighbors and self.next_head_position(self.head(), "left") not in self.bodies:
                result.add("left")
            if self.next_head_position(self.head(), "down") in enemy_head_neighbors and self.next_head_position(self.head(), "down") not in self.bodies:
                result.add("down")
        return result
    
    def enemy_head_direction(self, enemy_snake_data: typing.Self) -> set[str]:
        result = set()
        if enemy_snake_data.length() < self.length():
            if enemy_snake_data.head()[X] + 1 == self.head()[X] and enemy_snake_data.head()[Y] == self.head()[Y]:
                result.add("right")
            elif enemy_snake_data.head()[X] == self.head()[X] and enemy_snake_data.head()[Y] + 1 == self.head()[Y]:
                result.add("up")
            elif enemy_snake_data.head()[X] - 1 == self.head()[X] and enemy_snake_data.head()[Y] == self.head()[Y]    :
                result.add("left")
            elif enemy_snake_data.head()[X] == self.head()[X] and enemy_snake_data.head()[Y] - 1 == self.head()[Y]:
                result.add("down")
        return result
        
        