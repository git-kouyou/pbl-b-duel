from __future__ import annotations
import typing
from collections import deque
from enum import Enum

X = 0
Y = 1

# 盤面上の各マスの種類
class Type(Enum):
    safe = 0
    food = -1
    body = 1
    wall = 100
    enemy_head_predict = 200

class Status(Enum):
    loop = 0
    eat_food = 1

# データクラス
class BoardData:
    height: int
    width: int
    is_initialized: bool = False
    previous_foods: set[tuple[int, int]] = set()

    def __init__(self, game_state: typing.Dict):
        if not BoardData.is_initialized:
            BoardData.is_initialized = True
            BoardData.height = game_state["board"]["height"]
            BoardData.width = game_state["board"]["width"]
        self.foods = set([(food["x"], food["y"]) for food in game_state["board"]["food"]])
        self.each_snake_bodies = [[(body["x"], body["y"]) for body in snake["body"]] for snake in game_state["board"]["snakes"]]

        if len(game_state["board"]["snakes"]) == 1:
            snake_data_input = game_state["board"]["snakes"][0]
            enemy_snake_data = EnemySnakeData(snake_data_input)
            my_snake_data = MySnakeData(board_data=self, my_snake_data_input=snake_data_input, enemy_snake_data=snake_data_input)
        elif len(game_state["board"]["snakes"]) == 0:
            return
        else:
            if game_state["board"]["snakes"][0]["id"] == game_state["you"]["id"]:
                my_snake_data_input = game_state["board"]["snakes"][0]
                enemy_snake_data_input = game_state["board"]["snakes"][1]

                enemy_snake_data = EnemySnakeData(enemy_snake_data=enemy_snake_data_input)
                my_snake_data = MySnakeData(board_data=self, my_snake_data_input=my_snake_data_input, enemy_snake_data=enemy_snake_data)
            else:
                my_snake_data_input = game_state["board"]["snakes"][1]
                enemy_snake_data_input = game_state["board"]["snakes"][0]

                enemy_snake_data = EnemySnakeData(enemy_snake_data=enemy_snake_data_input)
                my_snake_data = MySnakeData(board_data=self, my_snake_data_input=my_snake_data_input, enemy_snake_data=enemy_snake_data)

        self.enemy_snake_data = enemy_snake_data
        self.my_snake_data = my_snake_data

        self.generate_board()

    def generate_board(self):
        self.board = [[Type.safe.value] * (BoardData.width) for _ in range(BoardData.height)]
        for food in self.foods:
            self.board[food[Y]][food[X]] = Type.food.value
        for bodies in self.each_snake_bodies:
            ate_food = 0 # 餌を食べた時の盤面の補正
            if bodies[0] in BoardData.previous_foods:
                ate_food = 1
            for i, body in enumerate(list(bodies)[:-1]):
                self.board[body[Y]][body[X]] = len(bodies) - i + Type.body.value - 1 + ate_food  # 頭に近いほど値が大きい
        if self.my_snake_data.length() <= self.enemy_snake_data.length():
            for pos in self.enemy_snake_data.head_around():
                if pos == self.enemy_snake_data.neck():
                    continue
                self.board[pos[Y]][pos[X]] = Type.enemy_head_predict.value

    def is_reachable(self, start: tuple[int, int], goal: tuple[int, int]) -> int:
        if start == goal:
            return 0
 
        visited = [[False] * BoardData.width for _ in range(BoardData.height)]
        visited[start[Y]][start[X]] = True

        queue = deque([(start[X], start[Y], 0)])
        while queue:
            x, y, depth = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                nd = depth + 1
                if 0 <= nx < BoardData.width and 0 <= ny < BoardData.height and not visited[ny][nx]:
                    if self.board[ny][nx] <= nd:
                        if (nx, ny) == goal:
                            return nd
                        visited[ny][nx] = True
                        queue.append((nx, ny, nd))
        return 10000
    
    def is_reachable_food_avoidance(self, start: tuple[int, int], goal: tuple[int, int]) -> int:
        if start == goal:
            return 0
        if self.board[start[Y]][start[X]] == Type.food.value or self.board[goal[Y]][goal[X]] == Type.food.value:
            return 10000
        visited = [[False] * BoardData.width for _ in range(BoardData.height)]
        visited[start[Y]][start[X]] = True

        queue = deque([(start[X], start[Y], 0)])
        while queue:
            x, y, depth = queue.popleft()
            nd = depth + 1
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < BoardData.width and 0 <= ny < BoardData.height and not visited[ny][nx]:
                    if 0 <= self.board[ny][nx] <= nd:
                        if (nx, ny) == goal:
                            return nd
                        visited[ny][nx] = True
                        queue.append((nx, ny, nd))
        return 10000
    
    def is_reachable_enemy_tail(self, direction) -> int:
        return self.is_reachable(self.my_snake_data.next_head_position(self.my_snake_data.head(), direction), self.enemy_snake_data.tail())
    
    def is_reachable_my_tail(self, direction) -> int:
        return self.is_reachable(self.my_snake_data.next_head_position(self.my_snake_data.head(), direction), self.my_snake_data.tail())
    
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
        
    def foods_only_you_can_reach(self) -> set[tuple[int, int]]:
        result = set()
        for food in self.foods:
            distance_between_your_snake = self.is_reachable(self.my_snake_data.head(), food)
            distance_between_enemy_snake = self.is_reachable(self.enemy_snake_data.head(), food)
            if self.my_snake_data.length() <= self.enemy_snake_data.length():
                if distance_between_your_snake < distance_between_enemy_snake:
                    result.add(food)
            else:
                if distance_between_your_snake <= distance_between_enemy_snake:
                    result.add(food)
        return result
    
    def point_direction(self, direction: str) -> int:
        my_snake_data = self.my_snake_data
        enemy_snake_data = self.enemy_snake_data
        max_distance = BoardData.width + BoardData.height + 2
        point = 0

        # 進む方向のオフセット
        if direction == "up":
            offset = (0, 1)
        elif direction == "left":
            offset = (-1, 0)
        elif direction == "down":
            offset = (0, -1)
        elif direction == "right":
            offset = (1, 0)
        else:
            return 0

        #進行不可能方向なら0点
        if direction in my_snake_data.unsafes_around():
            return point
        
        #到達可能判定
        distance_from_enemy_tail = self.is_reachable_enemy_tail(direction)
        distance_from_my_tail = self.is_reachable_my_tail(direction)

        #敵の尾に到達可能、自分の尾に到達可能なら加点
        if distance_from_enemy_tail < 10000 or distance_from_my_tail < 10000:
            point += 200
        
        #自分のみ到達できる餌に近づく場合加点
        for food in self.foods_only_you_can_reach():
            #餌に近づけば加点
            distance_food_after_move = self.is_reachable(my_snake_data.next_head_position(my_snake_data.head(), direction), food)

            distance_food_my_snake = self.is_reachable(my_snake_data.head(), food)
            # distance_food_enemy_snake = self.is_reachable(enemy_snake_data.head(), food)
            
            if distance_food_after_move < 10000:
                #餌への距離が近いほど加点
                distance_food_my_snake = self.is_reachable(my_snake_data.head(), food)
                distance_offset = max_distance - (distance_food_my_snake / 2)

                point += 4 * distance_offset # * ((distance_from_my_snake - distance_from_enemy_snake) + 1)

        #餌に近づくと加点(ただし敵に近いやつはそこまで加点しない)
        if self.foods_only_you_can_reach():
            for food in self.foods:
                #餌に近づけば加点
                approach_offset = offset[X] * (food[X] - my_snake_data.head()[X]) + offset[Y] * (food[Y] - my_snake_data.head()[Y])
                
                if approach_offset > 0:
                    #餌への距離が近いほど加点
                    distance_from_my_snake = abs(my_snake_data.head()[X] - food[X]) + abs(my_snake_data.head()[Y] - food[Y])
                    distance_offset = max_distance - distance_from_my_snake
                    point += distance_offset

        if my_snake_data.length() <= enemy_snake_data.length():
            #自分の尾に近づくと加点
            my_tail_offset = offset[X] * (my_snake_data.tail()[X] - my_snake_data.head()[X]) + offset[Y] * (my_snake_data.tail()[Y] - my_snake_data.head()[Y])
            if my_tail_offset > 0:
                point += 10
            
            #敵の尾に近づくと加点
            enemy_tail_offset = offset[X] * (enemy_snake_data.tail()[X] - my_snake_data.head()[X]) + offset[Y] * (enemy_snake_data.tail()[Y] - my_snake_data.head()[Y])
            if enemy_tail_offset > 0:
                point += 10

            #敵の頭に近づくと減点
            enemy_head_offset = offset[X] * (enemy_snake_data.head()[X] - my_snake_data.head()[X]) + offset[Y] * (enemy_snake_data.head()[Y] - my_snake_data.head()[Y])
            if 0 < enemy_head_offset < 5:
                point -= 10
        else:
            #自分の尾に近づくと加点
            my_tail_offset = offset[X] * (my_snake_data.tail()[X] - my_snake_data.head()[X]) + offset[Y] * (my_snake_data.tail()[Y] - my_snake_data.head()[Y])
            
            #敵の尾に近づくと加点
            enemy_tail_offset = offset[X] * (enemy_snake_data.tail()[X] - my_snake_data.head()[X]) + offset[Y] * (enemy_snake_data.tail()[Y] - my_snake_data.head()[Y])
            if enemy_tail_offset > 0 or my_tail_offset > 0:
                point += 15

            #敵の頭に近づくと減点
            enemy_head_offset = offset[X] * (enemy_snake_data.head()[X] - my_snake_data.head()[X]) + offset[Y] * (enemy_snake_data.head()[Y] - my_snake_data.head()[Y])
            if enemy_head_offset > 0:
                point -= 10

        return point
    
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
        if self.head()[X] + 1 < BoardData.width:
            result.add((self.head()[X] + 1, self.head()[Y]))
        if self.head()[X] - 1 >= 0:
            result.add((self.head()[X] - 1, self.head()[Y]))
        if self.head()[Y] + 1 < BoardData.height:
            result.add((self.head()[X], self.head()[Y] + 1))
        if self.head()[Y] - 1 >= 0:
            result.add((self.head()[X], self.head()[Y] - 1))
        return result

class MySnakeData:
    previous_foods:typing.Set[typing.Tuple[int, int]]
    status: Status = Status.loop
    disignated_route: deque
    isDisignated: bool
    initialized = False

    def __init__(self, board_data: BoardData, my_snake_data_input, enemy_snake_data: EnemySnakeData):

        # 初生成時にクラス変数を初期化
        if not MySnakeData.initialized:
            # GameData.previous_foods = set((food["x"], food["y"]) for food in game_state["board"]["food"])
            MySnakeData.status = Status.loop
            #初期化済み
            MySnakeData.initialized = True
            print(f"Snake:{my_snake_data_input['name']}Data initialized")

        # 体の座標(tuple)一覧
        self.bodies = deque()
        self.board_data = board_data
        seen = set()
        for body in my_snake_data_input["body"]:
            pos = (body["x"], body["y"])
            if pos not in seen:
                seen.add(pos)
                self.bodies.append(pos)
  
        # 残り体力
        self.health = my_snake_data_input["health"]

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
        board = self.board_data.board
        if 0 <= head[X] + 1 < BoardData.width and (board[head[Y]][head[X] + 1] <= Type.safe.value or board[head[Y]][head[X] + 1] == Type.enemy_head_predict.value):
            result.add("right")
        if 0 <= head[Y] + 1 < BoardData.height and (board[head[Y] + 1][head[X]] <= Type.safe.value or board[head[Y] + 1][head[X]] == Type.enemy_head_predict.value):
            result.add("up")
        if 0 <= head[X] - 1 < BoardData.width and (board[head[Y]][head[X] - 1] <= Type.safe.value or board[head[Y]][head[X] - 1] == Type.enemy_head_predict.value):
            result.add("left")
        if 0 <= head[Y] - 1 < BoardData.height and (board[head[Y] - 1][head[X]] <= Type.safe.value or board[head[Y] - 1][head[X]] == Type.enemy_head_predict.value):
            result.add("down")
        return result
    
    # 進行不可能方向(潜在的な詰み含む)のリスト
    def unsafes_around(self) -> set[str]:
        result = set()
        head = self.head()
        board = self.board_data.board 
        if head[X] + 1 >= BoardData.width or board[head[Y]][head[X] + 1] >= Type.body.value + 1:
            result.add("right")
        if head[Y] + 1 >= BoardData.height or board[head[Y] + 1][head[X]] >= Type.body.value + 1:
            result.add("up")
        if  head[X] - 1 < 0 or board[head[Y]][head[X] - 1] >= Type.body.value + 1:
            result.add("left")
        if head[Y] - 1 < 0 or board[head[Y] - 1][head[X]] >= Type.body.value + 1:
            result.add("down")

        return result
    
    # 周りの餌のある方向のリスト
    def foods_around(self) -> set[str]:
        result = set()
        head = self.head()
        board = self.board_data.board
        if 0 <= head[X] + 1 < BoardData.width and board[head[Y]][head[X] + 1] == Type.food.value:
            result.add("right")
        if 0 <= head[Y] + 1 < BoardData.height and board[head[Y] + 1][head[X]] == Type.food.value:
            result.add("up")
        if 0 <= head[X] - 1 < BoardData.width and board[head[Y]][head[X] - 1] == Type.food.value:
            result.add("left")
        if 0 <= head[Y] - 1 < BoardData.height and board[head[Y] - 1][head[X]] == Type.food.value:
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
        
        