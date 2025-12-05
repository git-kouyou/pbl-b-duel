import typing
from collections import deque
from enum import Enum

X = 0
Y = 1

class Status(Enum):
    loop = 0
    eat_food = 1

# 盤面上の各マスの種類
class Type(Enum):
    safe = 0
    food = -1
    body = 1
    wall = 100

# データクラス
class BoardData:
    height: int
    width: int
    is_initialized: bool = False

    def __init__(self, game_state: typing.Dict):
        if not BoardData.is_initialized:
            BoardData.is_initialized = True
            BoardData.height = game_state["board"]["height"]
            BoardData.width = game_state["board"]["width"]
        self.foods = set([(food["x"], food["y"]) for food in game_state["board"]["food"]])
        self.each_snake_bodies = [[(body["x"], body["y"]) for body in snake["body"]] for snake in game_state["board"]["snakes"]]
        self.generate_board()

    def generate_board(self):
        self.board = [[Type.safe.value] * (BoardData.width) for _ in range(BoardData.height)]
        for food in self.foods:
            self.board[food[Y]][food[X]] = Type.food.value
        for bodies in self.each_snake_bodies:
            for i, body in enumerate(list(bodies)[:-1]):
                self.board[body[Y]][body[X]] = len(bodies) - i + Type.body.value - 2  # 頭に近いほど値が大きい
    
    # デバッグ用盤面表示
    def print_board(self):
        for y in reversed(range(BoardData.height)):
            row = ""
            for x in range(BoardData.width):
                if self.board[y][x] != Type.wall.value:
                    row += f"{self.board[y][x]}".zfill(2) + " "
                else:
                    row += "## "
            print(row)
    
    # 向きの反転
    def reverse_direction(self, direction: str) -> str:
        if direction == "up":
            return "down"
        elif direction == "down":
            return "up"
        elif direction == "left":
            return "right"
        else:
            return "left"

class SnakeData:
    previous_foods:typing.Set[typing.Tuple[int, int]]
    status: Status = Status.loop
    disignated_route: deque
    isDisignated: bool
    initialized = False

    def __init__(self, board_data: BoardData, snake_data, bodies = set(), foods = []):
        if snake_data == {} and bodies == []:
            print("cannot initialize GameData!")
            exit(1)

        # 初生成時にクラス変数を初期化
        if not SnakeData.initialized:
            # GameData.previous_foods = set((food["x"], food["y"]) for food in game_state["board"]["food"])
            SnakeData.status = Status.loop
            #初期化済み
            SnakeData.initialized = True
            print(f"Snake:{snake_data['name']}Data initialized")

        # 盤面情報
        self.board = board_data.board
        # 体の座標(tuple)一覧
        self.bodies = deque()
        if not bodies:
            seen = set()
            for body in snake_data["body"]:
                pos = (body["x"], body["y"])
                if pos not in seen:
                    seen.add(pos)
                    self.bodies.append(pos)
        else:
            self.bodies = bodies
        # 食べ物の座標(tuple)一覧
        self.foods = board_data.foods
        # 残り体力
        self.health = snake_data["health"]

    # 餌を食べた直後ならばTrueを返す
    def ate_food(self):
        return self.previous_foods != self.foods

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
    def empty_around(self):
        result = []
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] <= Type.safe.value:
            result.append("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] <= Type.safe.value:
            result.append("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] <= Type.safe.value:
            result.append("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] <= Type.safe.value:
            result.append("down")
        return result
    
    # 進行不可能方向(潜在的な詰み含む)のリスト
    def unsafes_around(self):
        result = []
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] >= Type.body.value + 1:
            result.append("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] >= Type.body.value + 1:
            result.append("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] >= Type.body.value + 1:
            result.append("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] >= Type.body.value + 1:
            result.append("down")
        return result
    
    # 周りの餌のある方向のリスト
    def foods_around(self):
        result = []
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] == Type.food.value:
            result.append("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] == Type.food.value:
            result.append("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] == Type.food.value:
            result.append("left")
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] == Type.food.value:
            result.append("down")
        return result
    
    # 周りの安全な方向のリスト
    def safes_around(self):
        result = [] 
        head = self.head()
        if 0 <= head[X] + 1 < BoardData.width and self.board[head[Y]][head[X] + 1] <= Type.safe.value:
            result.append("right")
        if 0 <= head[Y] + 1 < BoardData.height and self.board[head[Y] + 1][head[X]] <= Type.safe.value:
            result.append("up")
        if 0 <= head[X] - 1 < BoardData.width and self.board[head[Y]][head[X] - 1] <= Type.safe.value:
            result.append("left")   
        if 0 <= head[Y] - 1 < BoardData.height and self.board[head[Y] - 1][head[X]] <= Type.safe.value:
            result.append("down")
        return result
    
    # 餌のない安全な方向のリスト
    def no_foods(self):
        return list(set(self.safes_around()) - set(self.foods_around()))
    
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
        