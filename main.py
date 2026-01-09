# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
from collections import deque


def info() -> typing.Dict:
    print("INFO")
    return {
        "apiversion": "1",
        "author": "",
        "color": "#243682",
        "head": "default",
        "tail": "default",
    }

def start(game_state: typing.Dict):
    print("GAME START")

def end(game_state: typing.Dict):
    print("GAME OVER\n")

def to_tuple(cell):
    return (cell["x"], cell["y"])

def neighbors4(x, y):
    return [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]

def open_degree(x, y, board_width, board_height, blocked_set):
    deg = 0
    for nx, ny in neighbors4(x, y):
        if 0 <= nx < board_width and 0 <= ny < board_height and (nx, ny) not in blocked_set:
            deg += 1
    return deg

def flood_fill_area_limited(start_xy, board_width, board_height, blocked_set, limit):
    """到達可能面積を数える（limit到達で早期終了）"""
    visited = set()
    stack = [start_xy]
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if len(visited) >= limit:
            return limit
        for nx, ny in neighbors4(x, y):
            if 0 <= nx < board_width and 0 <= ny < board_height and (nx, ny) not in blocked_set and (nx, ny) not in visited:
                stack.append((nx, ny))
    return len(visited)

def evaluate_state(my_head, board_width, board_height, obstacles_set, food, health):
    hx, hy = my_head["x"], my_head["y"]
    if hx < 0 or hx >= board_width or hy < 0 or hy >= board_height:
        return -9999
    if (hx, hy) in obstacles_set:
        return -9999

    # 食べ物スコア（近いほど良い）
    food_score = 0
    if food:
        dist = min(abs(f["x"] - hx) + abs(f["y"] - hy) for f in food)
        food_score = 50 - dist

    # 空きスペース（早期打ち切り版）
    area_score = flood_fill_area_limited((hx, hy), board_width, board_height, obstacles_set, limit=50)

    # 体力が少ないほど食べ物重視（軽い係数）
    health_score = -max(0, 100 - health) * 0.2

    return food_score + area_score + health_score

def bfs_shortest_path(start, goals, board_width, board_height, blocked_set):
    """
    start: (x, y)
    goals: set([(x,y), ...]) 食べ物の座標セット
    blocked_set: 障害物（自分・相手の体）
    """
    queue = deque([start])
    visited = {start: None}  # どこから来たかを記録

    while queue:
        x, y = queue.popleft()

        # ゴールに到達したら経路を復元
        if (x, y) in goals:
            path = []
            cur = (x, y)
            while cur is not None:
                path.append(cur)
                cur = visited[cur]
            path.reverse()
            return path  # 最短経路のリスト

        for nx, ny in neighbors4(x, y):
            if 0 <= nx < board_width and 0 <= ny < board_height:
                if (nx, ny) not in blocked_set and (nx, ny) not in visited:
                    visited[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

    return None  # 食べ物に行けない

def minimax(my_head, depth, board_width, board_height, obstacles_set, food, health, is_maximizing):
    if depth == 0:
        return evaluate_state(my_head, board_width, board_height, obstacles_set, food, health)

    moves = [
        {"x": my_head["x"]+1, "y": my_head["y"]},
        {"x": my_head["x"]-1, "y": my_head["y"]},
        {"x": my_head["x"], "y": my_head["y"]+1},
        {"x": my_head["x"], "y": my_head["y"]-1}
    ]

    if is_maximizing:
        best_value = -9999
        for m in moves:
            hx, hy = m["x"], m["y"]
            if hx < 0 or hx >= board_width or hy < 0 or hy >= board_height:
                continue
            if (hx, hy) in obstacles_set:
                continue
            val = minimax(m, depth-1, board_width, board_height, obstacles_set, food, health-1, False)
            if val > best_value:
                best_value = val
        return best_value
    else:
        worst_value = 9999
        for m in moves:
            hx, hy = m["x"], m["y"]
            if hx < 0 or hx >= board_width or hy < 0 or hy >= board_height:
                continue
            if (hx, hy) in obstacles_set:
                continue
            val = minimax(m, depth-1, board_width, board_height, obstacles_set, food, health-1, True)
            if val < worst_value:
                worst_value = val
        return worst_value if worst_value != 9999 else evaluate_state(my_head, board_width, board_height, obstacles_set, food, health)

def move(game_state: typing.Dict) -> typing.Dict:
    you = game_state["you"]
    my_head = you["body"][0]
    my_neck = you["body"][1] if len(you["body"]) > 1 else my_head
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    opponents = game_state['board']['snakes']
    food = game_state['board']['food']
    health = you["health"]

    # 候補手
    possible_moves = {
        "up":    {"x": my_head["x"],     "y": my_head["y"] + 1},
        "down":  {"x": my_head["x"],     "y": my_head["y"] - 1},
        "left":  {"x": my_head["x"] - 1, "y": my_head["y"]},
        "right": {"x": my_head["x"] + 1, "y": my_head["y"]}
    }

    # 基本障害物（全スネークの体）
    obstacles_set = set()
    for snake in opponents:
        for part in snake['body']:
            obstacles_set.add(to_tuple(part))

    # 後退禁止
    banned = set()
    if my_neck["x"] < my_head["x"]:
        banned.add("left")
    elif my_neck["x"] > my_head["x"]:
        banned.add("right")
    elif my_neck["y"] < my_head["y"]:
        banned.add("down")
    elif my_neck["y"] > my_head["y"]:
        banned.add("up")
     # 相手頭の次可能位置を危険扱い(相手の長さによって変える予定)
    danger_set = set()
    for snake in opponents:
        if snake["id"] == you["id"]:
            continue
        hx, hy = snake["body"][0]["x"], snake["body"][0]["y"]
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            danger_set.add((hx+dx, hy+dy))

    prelim_safe = []
    for mv, coord in possible_moves.items():
        if mv in banned:
            continue
        x, y = coord["x"], coord["y"]
        if not (0 <= x < board_width and 0 <= y < board_height):
            continue
        if (x, y) in obstacles_set:  # 自分/他の体
            continue
        if (x, y) in danger_set:     # 相手頭危険域
            continue
        prelim_safe.append(mv)
    

    # 自分の尾（次ターンに動く可能性）を条件付きで除外して袋小路面積を少し楽観視
    your_body = you["body"]
    your_tail_tuple = to_tuple(your_body[-1]) if your_body else None

    # 袋小路・自由度チェック
    safe_moves = []
    for mv in prelim_safe:
        coord = possible_moves[mv]
        x, y = coord["x"], coord["y"]

        # 食べ物を踏むかどうか（踏むなら尾は伸びる＝尾除外をしない）
        stepping_food = any(f["x"] == x and f["y"] == y for f in food)

        # 面積評価用の障害物集合（自分の尾を条件付きで外す）
        area_blocked = set(obstacles_set)
        if your_tail_tuple and not stepping_food:
            # 次ターン尾が動く前提で、少し通路が広がる可能性を反映
            if your_tail_tuple in area_blocked:
                area_blocked.remove(your_tail_tuple)

        # 隣接自由度（デッドエンド判定）
        deg = open_degree(x, y, board_width, board_height, area_blocked)
        # 体力が十分あるときは自由度1以下の死地を避ける
        if deg <= 1 and health > 20 and not stepping_food:
            continue

        # 到達面積（動的閾値）
        # 体力高→広い面積を要求、体力低→緩める
        base_thresh = 8 if health >= 40 else 4
        # 終盤や大蛇ほど広さが必要（体長の影響を少し足す）
        length_factor = max(0, len(you["body"]) // 4)
        area_threshold = base_thresh + length_factor

        area_size = flood_fill_area_limited((x, y), board_width, board_height, area_blocked, limit=area_threshold)
        if area_size < area_threshold:
            continue

        safe_moves.append(mv)

    # それでも安全手がない場合、最小限の条件でフォールバック
    if not safe_moves:
        fallback = []
        for mv, coord in possible_moves.items():
            if mv in banned:
                continue
            x, y = coord["x"], coord["y"]
            if not (0 <= x < board_width and 0 <= y < board_height):
                continue
            if (x, y) in obstacles_set:
                continue
            fallback.append(mv)
        if fallback:
            next_move = random.choice(fallback)
            print(f"MOVE {game_state['turn']}: {next_move} (fallback)")
            return {"move": next_move}
        print(f"MOVE {game_state['turn']}: down (no-safe)")
        return {"move": "down"}

    # ミニマックスで安全候補のみ評価
    best_move = None
    best_value = -9999
    for mv in safe_moves:
        coord = possible_moves[mv]
        val = minimax(coord, depth=2, board_width=board_width, board_height=board_height,
                      obstacles_set=obstacles_set, food=food, health=health, is_maximizing=True)
        if val > best_value:
            best_value = val
            best_move = mv

    # 体力が少ないとき、同点なら食べ物に寄る手を優先
    if health < 30 and food:
        closest = min(food, key=lambda f: abs(f["x"] - my_head["x"]) + abs(f["y"] - my_head["y"]))
        tx, ty = closest["x"], closest["y"]
        greedy = None
        if tx < my_head["x"] and "left" in safe_moves: greedy = "left"
        elif tx > my_head["x"] and "right" in safe_moves: greedy = "right"
        elif ty < my_head["y"] and "down" in safe_moves: greedy = "down"
        elif ty > my_head["y"] and "up" in safe_moves: greedy = "up"
        if greedy and best_move is not None:
            # ミニマックス評価が近い場合のみ切り替え（過度な突撃を緩和）
            if best_value > -9000:
                best_move = greedy

    if best_move is None:
        best_move = random.choice(safe_moves)

    print(f"MOVE {game_state['turn']}: {best_move} (score={best_value})")
    return {"move": best_move}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})