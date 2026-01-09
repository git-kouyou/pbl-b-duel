# 6班duel ソースコード
# python version: 3.13.3

import random
import typing
from reachable import Reachable
from gamedata import SnakeData, BoardData, Type

X = 0
Y = 1

DEBUG = True

def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "6",  # TODO: Your Battlesnake Username
        "color": "#FFC0CB",  # TODO: Choose color pink
        "head": "pig",  # TODO: Choose head
        "tail": "football",  # TODO: Choose tail
    }

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    BoardData.is_initialized = False
    BoardData(game_state)
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

def next_move(board_data: BoardData, your_snake_data: SnakeData, enemy_snake_data: SnakeData) -> str:
    next_move = "None"
    safes_around = your_snake_data.safes_around()
    sorted_foods = sorted(list(your_snake_data.foods), key=lambda f: abs(f[X] - your_snake_data.head()[X]) + abs(f[Y] - your_snake_data.head()[Y]))
    closest_food = min(sorted_foods) if sorted_foods else None
    kill_moves = [m for m in your_snake_data.safes_around() if board_data.board[your_snake_data.next_head_position(your_snake_data.head(), m)[Y]][your_snake_data.next_head_position(your_snake_data.head(), m)[X]] <= Type.kill.value]

    #体が極小の時: 優先度1
    if your_snake_data.length() <= 2:
        if your_snake_data.no_foods():
            next_move = random.choice(your_snake_data.no_foods())
        elif your_snake_data.safes_around():
            next_move = random.choice(your_snake_data.safes_around())
        return next_move
    
    bfs = Reachable(board_data)
    reachable_food_avoidance = []
    reachable = []
    my_tail = your_snake_data.tail()
    enemy_tail_reachable = []
    enemy_tail = enemy_snake_data.tail()
    if your_snake_data.length() >= 3:
        board_data.board[enemy_tail[Y]][enemy_tail[X]] = Type.body.value  # 自分の尾を体判定に変更
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bfs.is_reachable_food_avoidance(next_head, your_snake_data.tail()):
                reachable_food_avoidance.append(move)
            if bfs.is_reachable(next_head, your_snake_data.tail()):
                reachable.append(move)
        board_data.board[enemy_tail[Y]][enemy_tail[X]] = Type.safe.value
        
    #体が極小の時: 優先度1
    if your_snake_data.length() <= 2:
        if your_snake_data.no_foods():
            next_move = random.choice(your_snake_data.no_foods())
        elif your_snake_data.safes_around():
            next_move = random.choice(your_snake_data.safes_around())
        return next_move
    
    #head-to-head
    if kill_moves:
        kill_safe_moves = [m for m in kill_moves if m in reachable]
        if kill_safe_moves:
            next_move = random.choice(kill_safe_moves)
            if DEBUG:
                print(f"Executing kill move: {next_move}")
            return next_move
    
    #体の長さが7になるまで or 体力が少ないとき
    if(your_snake_data.length() <= 7 or your_snake_data.health <= your_snake_data.manhattan_distance(closest_food)*2):
        for food_target in sorted_foods:
        
            target_moves = []
            head = your_snake_data.head()
            tx, ty = food_target
        
        # 餌の方向を特定
            if tx > head[X] and 'right' in safes_around: target_moves.append('right')
            if tx < head[X] and 'left' in safes_around: target_moves.append('left')
            if ty > head[Y] and 'up' in safes_around: target_moves.append('up')
            if ty < head[Y] and 'down' in safes_around: target_moves.append('down')

            target_safe_moves = [m for m in target_moves if m in reachable]

            if target_safe_moves:
                next_move = random.choice(target_safe_moves)
                if DEBUG: 
                    print(f"Targeting food at {food_target} with move {next_move}")
                return next_move

    # 相手の尾追い
    if your_snake_data.length() >= enemy_snake_data.length():
        board_data.board[my_tail[Y]][my_tail[X]] = Type.body.value  # 自分の尾を体判定に変更
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bfs.is_reachable(next_head, enemy_tail):
                if DEBUG:
                    print(f"reachable list added")
                enemy_tail_reachable.append(move)

        board_data.board[my_tail[Y]][my_tail[X]] = Type.safe.value  # 自分の尾を体判定に変更
        """
        tx, ty = enemy_tail
        head = your_snake_data.head()

        if tx > head[X] and 'right' in safes_around: enemy_tail_reachable.append('right')
        if tx < head[X] and 'left' in safes_around: enemy_tail_reachable.append('left')
        if ty > head[Y] and 'up' in safes_around: enemy_tail_reachable.append('up')
        if ty < head[Y] and 'down' in safes_around: enemy_tail_reachable.append('down')
        """
        """
        if reachable:
            next_move = random.choice(reachable)
            return next_move
        """
    # ここまで追加部分
    
    if enemy_tail_reachable:
        next_move = random.choice(enemy_tail_reachable)
        if next_move not in reachable:
            if reachable:
                if DEBUG:
                    print("Enemy tail reachable moves not reachable, choosing random reachable move")
                next_move = random.choice(reachable)
                return next_move
            else:
                if DEBUG:
                    print("Enemy tail reachable moves not reachable, but no reachable moves available")
                next_move = random.choice(safes_around)
                return next_move
        else:
            if DEBUG:
                print(f"Chasing enemy tail with move {next_move}")
            return next_move
    
    if reachable:
        next_move = random.choice(reachable)
        if DEBUG:
            print("Choosing random reachable move")
        return next_move
    
    if reachable_food_avoidance:
        next_move = random.choice(reachable_food_avoidance)
        if DEBUG:
            print("Choosing random reachable_food_avoidance move")
        return next_move
    
    if next_move == "None" and safes_around:
        next_move = random.choice(safes_around)
        if DEBUG:
            print("No reachable moves, choosing random safe move")
        return next_move

# 初期化やデバッグ表示など
def move(game_state: typing.Dict) -> typing.Dict:
    board_data = BoardData(game_state)
    your_snake_data = None
    enemy_snake_data = None
    for snake_data in game_state["board"]["snakes"]:
        if snake_data["id"] == game_state["you"]["id"]:
            your_snake_data = SnakeData(board_data=board_data, snake_data=snake_data)
        else:
            enemy_snake_data = SnakeData(board_data=board_data, snake_data=snake_data)

    if enemy_snake_data is None:
        enemy_snake_data = your_snake_data
    reachable_food_avoidance = []
    reachable = []
    enemy_tail_reachable = []
    # 相手の尾追い
    if your_snake_data.length() >= enemy_snake_data.length() - 3:
        enemy_tail = enemy_snake_data.tail()

        bfs = Reachable(board_data)
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bfs.is_reachable(next_head, enemy_tail):
                if DEBUG:
                    print(f"reachable list added")
                enemy_tail_reachable.append(move)
        
    if your_snake_data.length() >= 3:
        bfs = Reachable(board_data)
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bfs.is_reachable_food_avoidance(next_head, your_snake_data.tail()):
                reachable_food_avoidance.append(move)
            if bfs.is_reachable(next_head, your_snake_data.tail()):
                reachable.append(move)
    
    next_move_result = next_move(board_data, your_snake_data, enemy_snake_data)
    if next_move_result not in your_snake_data.safes_around():
        next_move_result = random.choice(your_snake_data.safes_around())

    if DEBUG:
        print(f"safes around: {your_snake_data.safes_around()}, no_foods around: {your_snake_data.no_foods()}")
        print(f"foods: {your_snake_data.foods}, bodies: {your_snake_data.bodies}")
        print(f"reachable: {reachable} reachable_food_avoidance: {reachable_food_avoidance} enemy_tail_reachable: {enemy_tail_reachable}")
        """print(f"target moves: {your_snake_data.target_moves()}")"""
        print(f"MOVE {game_state['turn']}: {next_move_result}")
        print(f"status: {SnakeData.status}")
        board_data.print_board()

    return {"move": next_move_result}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
