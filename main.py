# 6班solo ソースコード
# python version: 3.13.3

import random
import typing
from boarddata import BoardData
from snakedata import SnakeData

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

    reachable_your_tail = set()
    reachable_enemy_tail = set()
    approach_enemy_head = set()
    approach_enemy_tail = set()
    approach_your_tail = set()
    foods_sorted = set()
    approach_nearest_food = set()

    foods_sorted = sorted(
                board_data.foods_only_you_can_reach(your_snake_data, enemy_snake_data),
                key=lambda food: abs(your_snake_data.head()[X] - food[X]) + abs(your_snake_data.head()[Y] - food[Y]))

    for move in safes_around - your_snake_data.enemy_head_around(enemy_snake_data):
        next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
        if board_data.is_reachable(next_head, your_snake_data.tail()):
            reachable_your_tail.add(move)
        if board_data.is_reachable(next_head, enemy_snake_data.tail()):
            reachable_enemy_tail.add(move)

    if your_snake_data.head()[X] < enemy_snake_data.head()[X]:
            approach_enemy_head.add("right")
    if your_snake_data.head()[X] > enemy_snake_data.head()[X]:
        approach_enemy_head.add("left")
    if your_snake_data.head()[Y] < enemy_snake_data.head()[Y]:
        approach_enemy_head.add("up")
    if your_snake_data.head()[Y] > enemy_snake_data.head()[Y]:
        approach_enemy_head.add("down")

    if your_snake_data.head()[X] < enemy_snake_data.tail()[X]:
        approach_enemy_tail.add("right")
    if your_snake_data.head()[X] > enemy_snake_data.tail()[X]:
        approach_enemy_tail.add("left")
    if your_snake_data.head()[Y] < enemy_snake_data.tail()[Y]:
        approach_enemy_tail.add("up")
    if your_snake_data.head()[Y] > enemy_snake_data.tail()[Y]:
        approach_enemy_tail.add("down")

    if your_snake_data.head()[X] < your_snake_data.tail()[X]:
        approach_your_tail.add("right")
    if your_snake_data.head()[X] > your_snake_data.tail()[X]:
        approach_your_tail.add("left")
    if your_snake_data.head()[Y] < your_snake_data.tail()[Y]:
        approach_your_tail.add("up")
    if your_snake_data.head()[Y] > your_snake_data.tail()[Y]:
        approach_your_tail.add("down")

    if foods_sorted:
        if your_snake_data.head()[X] < foods_sorted[0][X]:
            approach_nearest_food.add("right")
        if your_snake_data.head()[X] > foods_sorted[0][X]:
            approach_nearest_food.add("left")
        if your_snake_data.head()[Y] < foods_sorted[0][Y]:
            approach_nearest_food.add("up")
        if your_snake_data.head()[Y] > foods_sorted[0][Y]:
            approach_nearest_food.add("down")

    #体が極小の時: 優先度1
    if your_snake_data.length() <= 2:
        if safes_around & approach_nearest_food:
            print("tire0")
            return random.choice(list(safes_around & approach_nearest_food))
    elif True or your_snake_data.length() > enemy_snake_data.length():
        safe = reachable_enemy_tail | reachable_your_tail
        if safe & approach_nearest_food:
            print("tire1")
            next_move = random.choice(list(safe & approach_nearest_food))
            return next_move
        elif safe:
            print("tire2")
            next_move = random.choice(list(safe))
            return next_move
    else:
        reachable_your_tail = set()
        reachable_enemy_tail = set()
        approach_enemy_tail = set()
        approach_nearest_food = set()

        for move in safes_around - your_snake_data.enemy_head_around(enemy_snake_data):
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if board_data.is_reachable(next_head, your_snake_data.tail()):
                reachable_your_tail.add(move)
            if board_data.is_reachable(next_head, enemy_snake_data.tail()):
                reachable_enemy_tail.add(move)

        if your_snake_data.head()[X] < enemy_snake_data.tail()[X]:
            approach_enemy_tail.add("right")
        if your_snake_data.head()[X] > enemy_snake_data.tail()[X]:
            approach_enemy_tail.add("left")
        if your_snake_data.head()[Y] < enemy_snake_data.tail()[Y]:
            approach_enemy_tail.add("up")
        if your_snake_data.head()[Y] > enemy_snake_data.tail()[Y]:
            approach_enemy_tail.add("down")

        if board_data.foods_only_you_can_reach(your_snake_data, enemy_snake_data):
            foods_sorted = sorted(
                board_data.foods_only_you_can_reach(your_snake_data, enemy_snake_data),
                key=lambda food: abs(your_snake_data.head()[X] - food[X]) + abs(your_snake_data.head()[Y] - food[Y])
            )
            if your_snake_data.head()[X] < foods_sorted[0][X]:
                approach_nearest_food.add("right")
            if your_snake_data.head()[X] > foods_sorted[0][X]:
                approach_nearest_food.add("left")
            if your_snake_data.head()[Y] < foods_sorted[0][Y]:
                approach_nearest_food.add("up")
            if your_snake_data.head()[Y] > foods_sorted[0][Y]:
                approach_nearest_food.add("down")
        
        print(f"reachable_your_tail: {reachable_your_tail}")
        print(f"reachable_enemy_tail: {reachable_enemy_tail}")
        print(f"approach_enemy_tail: {approach_enemy_tail}")
        print(f"approach_nearest_food: {approach_nearest_food}")

        if (reachable_your_tail & approach_enemy_tail & approach_nearest_food & reachable_enemy_tail):
            print("tire1")
            next_move = random.choice(list(reachable_your_tail & approach_enemy_tail & approach_nearest_food & reachable_enemy_tail))
            return next_move
        elif (reachable_your_tail & approach_nearest_food):
            print("tire2")
            next_move = random.choice(list(reachable_your_tail & approach_nearest_food))
            return next_move
        elif (reachable_your_tail & approach_enemy_tail & reachable_enemy_tail):
            print("tire3")
            next_move = random.choice(list(reachable_your_tail & approach_enemy_tail & reachable_enemy_tail))
            return next_move    
        elif (reachable_your_tail):
            print("tire4")
            next_move = random.choice(list(reachable_your_tail))
            return next_move
        
    if your_snake_data.empty_around():
        next_move = random.choice(list(your_snake_data.empty_around()))
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
    reachable = []
    if your_snake_data.length() >= 3:
        for move in your_snake_data.safes_around():
            next_head = your_snake_data.next_head_position(your_snake_data.head(), move)
            new_body = your_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if board_data.is_reachable(next_head, your_snake_data.tail()):
                reachable.append(move)
    
    next_move_result = next_move(board_data, your_snake_data, enemy_snake_data)

    if DEBUG:
        print(f"safes around: {your_snake_data.safes_around()}, no_foods around: {your_snake_data.no_foods()}")
        print(f"foods: {board_data.foods}, bodies: {your_snake_data.bodies}")
        print(f"foods only you can reach: {board_data.foods_only_you_can_reach(your_snake_data, enemy_snake_data)}")
        print(f"MOVE {game_state['turn']}: {next_move_result}")
        # board_data.print_board()

    BoardData.previous_foods = board_data.foods.copy()
    
    return {"move": next_move_result}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
