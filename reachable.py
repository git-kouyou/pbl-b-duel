from collections import deque
from gamedata import Type
from gamedata import X as X
from gamedata import Y as Y

# 盤面表現: board[y][x]

# BSFによる到達可能判定
class Reachable:
    def __init__(self, foods, bodies, width, height) -> None:
        self.width = width
        self.height = height
        self.board = self.generate_board(foods, bodies)

    def generate_board(self, foods, bodies):
        # 盤面を初期化
        result = [[0] * (self.width) for _ in range(self.height)]
        length = len(bodies)
        # 体
        for i, body in enumerate(bodies):
            if body[X] < 0 or body[Y] < 0:
                continue
            result[body[Y]][body[X]] = length - i
        # 食べ物
        for food in foods:
            result[food[Y]][food[X]] = Type.food.value
        return result

    def is_reachable(self, start: tuple[int, int], goal: tuple[int, int]) -> bool:
        if start == goal:
            return True
        visited = [[False] * self.width for _ in range(self.height)]
        visited[start[Y]][start[X]] = True

        queue = deque([(start[X], start[Y], 0)])
        while queue:
            x, y, depth = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                nd = depth + 1
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
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
        visited = [[False] * self.width for _ in range(self.height)]
        visited[start[Y]][start[X]] = True

        queue = deque([(start[X], start[Y], 0)])
        while queue:
            x, y, depth = queue.popleft()
            nd = depth + 1
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
                    if 0 <= self.board[ny][nx] <= nd:
                        if (nx, ny) == goal:
                            return True
                        visited[ny][nx] = True
                        queue.append((nx, ny, nd))
        return False
    
    # デバッグ用盤面表示
    def print_board(self):
        for y in reversed(range(self.height)):
            row = ""
            for x in range(self.width):
                row += f"{self.board[y][x]}".rjust(2) + " "
            print(row)
        print()
    
# デバッグ用
if __name__ == "__main__":
    DEBUG = True
    foods = []
    bodies = deque()

    BSF = Reachable(foods = foods, bodies = bodies, width = 6, height = 6)
    BSF.print_board()

    start = (0, 0)
    goal = (0, 0)

    print(f"reachable food avoid:{BSF.is_reachable_food_avoidance(start, goal)}")
    print(f"reachable:{BSF.is_reachable(start, goal)}")