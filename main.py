# 6班solo ソースコード
# python version: 3.13.3

import random
import typing
from reachable import Reachable
from gamedata import Status, SnakeData, BoardData

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
    if your_snake_data.length() >= 3:
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bfs.is_reachable_food_avoidance(next_head, your_snake_data.tail()):
                reachable_food_avoidance.append(move)
            if bfs.is_reachable(next_head, your_snake_data.tail()):
                reachable.append(move)
    
    if reachable:
        next_move = random.choice(reachable)
    elif reachable_food_avoidance:
        next_move = random.choice(reachable_food_avoidance)
    
    if next_move == "None" and safes_around:
        next_move = random.choice(safes_around)

    return next_move

# 初期化やデバッグ表示など
def move(game_state: typing.Dict) -> typing.Dict:
    board_data = BoardData(game_state)
    your_sanake_data = None
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

    if DEBUG:
        print(f"safes around: {your_snake_data.safes_around()}, no_foods around: {your_snake_data.no_foods()}")
        print(f"foods: {your_snake_data.foods}, bodies: {your_snake_data.bodies}")
        print(f"reachable: {reachable} reachable_food_avoidance: {reachable_food_avoidance}")
        print(f"MOVE {game_state['turn']}: {next_move_result}")
        print(f"status: {SnakeData.status}")
        board_data.print_board()
    return {"move": next_move_result}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
