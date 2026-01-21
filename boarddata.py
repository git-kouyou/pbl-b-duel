from __future__ import annotations
import typing
from typing import TYPE_CHECKING
from collections import deque
from enum import Enum

if TYPE_CHECKING:
    from snakedata import MySnakeData, EnemySnakeData

X = 0
Y = 1

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
    previous_foods: set[tuple[int, int]] = set()

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
            ate_food = 0 # 餌を食べた時の盤面の補正
            if bodies[0] in BoardData.previous_foods:
                ate_food = 1
            for i, body in enumerate(list(bodies)[:-1]):
                self.board[body[Y]][body[X]] = len(bodies) - i + Type.body.value - 2 + ate_food  # 頭に近いほど値が大きい

    def is_reachable(self, start: tuple[int, int], goal: tuple[int, int]) -> bool:
        if start == goal:
            return True
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
                            return True
                        visited[ny][nx] = True
                        queue.append((nx, ny, nd))
        return False
    
    def is_reachable_food_avoidance(self, start: tuple[int, int], goal: tuple[int, int]) -> bool:
        if start == goal:
            return True
        if self.board[start[Y]][start[X]] == Type.food.value or self.board[goal[Y]][goal[X]] == Type.food.value:
            return False
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
                            return True
                        visited[ny][nx] = True
                        queue.append((nx, ny, nd))
        return False
    
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
        
    def foods_only_you_can_reach(self, your_snake_data: MySnakeData, enemy_snake_data: EnemySnakeData) -> set[tuple[int, int]]:
        result = set()
        for food in self.foods:
            distance_between_your_snake = abs(your_snake_data.head()[X] - food[X]) + abs(your_snake_data.head()[Y] - food[Y])
            distance_between_enemy_snake = abs(enemy_snake_data.head()[X] - food[X]) + abs(enemy_snake_data.head()[Y] - food[Y])
            if distance_between_your_snake < distance_between_enemy_snake:
                result.add(food)
        return result