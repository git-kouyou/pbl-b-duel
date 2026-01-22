# 6班solo ソースコード
# python version: 3.13.3

import random
import typing
from gamedata import BoardData, MySnakeData, EnemySnakeData

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
    board_data = BoardData(game_state)
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

def next_move(board_data: BoardData, my_snake_data: MySnakeData, enemy_snake_data: EnemySnakeData) -> str:
    direction_points = {}
    safes_around = my_snake_data.safes_around()
    empty_around = my_snake_data.empty_around()

    if not safes_around:
        return random.choice(list(empty_around))
    else:
        for move in safes_around:
            direction_points[move] = board_data.point_direction(move)

        next_move = max(direction_points, key = lambda k: direction_points[k])

        if next_move:
            return next_move
        elif empty_around: 
            return random.choice(list(empty_around))
        else:
            return "up"
    
    next_move = "None"
    safes_around = my_snake_data.safes_around()

    reachable_your_tail = set()
    reachable_enemy_tail = set()
    approach_enemy_head = set()
    approach_enemy_tail = set()
    approach_your_tail = set()
    foods_sorted = set()
    approach_nearest_food = set()

    foods_sorted = sorted(
        board_data.foods_only_you_can_reach(),
        key=lambda food: ((abs(my_snake_data.head()[X] - food[X]) + abs(my_snake_data.head()[Y] - food[Y])) - (abs(enemy_snake_data.head()[X] - food[X]) + abs(enemy_snake_data.head()[Y] - food[Y]))))

    for move in safes_around:
        next_head = my_snake_data.next_head_position(my_snake_data.head(), move)
        print(next_head)
        if board_data.is_reachable(next_head, my_snake_data.tail()):
            reachable_your_tail.add(move)
        if board_data.is_reachable(next_head, enemy_snake_data.tail()):
            reachable_enemy_tail.add(move)

    if my_snake_data.head()[X] < enemy_snake_data.head()[X]:
        approach_enemy_head.add("right")
    if my_snake_data.head()[X] > enemy_snake_data.head()[X]:
        approach_enemy_head.add("left")
    if my_snake_data.head()[Y] < enemy_snake_data.head()[Y]:
        approach_enemy_head.add("up")
    if my_snake_data.head()[Y] > enemy_snake_data.head()[Y]:
        approach_enemy_head.add("down")

    if my_snake_data.head()[X] < enemy_snake_data.tail()[X]:
        approach_enemy_tail.add("right")
    if my_snake_data.head()[X] > enemy_snake_data.tail()[X]:
        approach_enemy_tail.add("left")
    if my_snake_data.head()[Y] < enemy_snake_data.tail()[Y]:
        approach_enemy_tail.add("up")
    if my_snake_data.head()[Y] > enemy_snake_data.tail()[Y]:
        approach_enemy_tail.add("down")

    if my_snake_data.head()[X] < my_snake_data.tail()[X]:
        approach_your_tail.add("right")
    if my_snake_data.head()[X] > my_snake_data.tail()[X]:
        approach_your_tail.add("left")
    if my_snake_data.head()[Y] < my_snake_data.tail()[Y]:
        approach_your_tail.add("up")
    if my_snake_data.head()[Y] > my_snake_data.tail()[Y]:
        approach_your_tail.add("down")

    if foods_sorted:
        if my_snake_data.head()[X] < foods_sorted[0][X]:
            approach_nearest_food.add("right")
        if my_snake_data.head()[X] > foods_sorted[0][X]:
            approach_nearest_food.add("left")
        if my_snake_data.head()[Y] < foods_sorted[0][Y]:
            approach_nearest_food.add("up")
        if my_snake_data.head()[Y] > foods_sorted[0][Y]:
            approach_nearest_food.add("down")

    #体が極小の時: 優先度1
    if my_snake_data.length() <= 2:
        if safes_around & approach_nearest_food:
            print("tire0")
            return random.choice(list(safes_around & approach_nearest_food))
    elif True or my_snake_data.length() > enemy_snake_data.length():
        safe = (reachable_enemy_tail | reachable_your_tail) & safes_around
        if safe & approach_nearest_food:
            print("tire1")
            next_move = random.choice(list(safe & approach_nearest_food))
            return next_move
        elif safe:
            print("tire2")
            next_move = random.choice(list(safe))
            return next_move
        
    if my_snake_data.empty_around():
        next_move = random.choice(list(my_snake_data.empty_around()))
    return next_move

# 初期化やデバッグ表示など
def move(game_state: typing.Dict) -> typing.Dict:
    board_data = BoardData(game_state)
    my_snake_data = board_data.my_snake_data
    enemy_snake_data = board_data.enemy_snake_data

    reachable = []
    if my_snake_data.length() >= 3:
        for move in my_snake_data.safes_around():
            next_head = my_snake_data.next_head_position(my_snake_data.head(), move)
            new_body = my_snake_data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if board_data.is_reachable(next_head, my_snake_data.tail()):
                reachable.append(move)
    
    next_move_result = next_move(board_data, my_snake_data, enemy_snake_data)

    if DEBUG:
        print(f"safes around: {my_snake_data.safes_around()}, no_foods around: {my_snake_data.no_foods()}")
        print(f"foods: {board_data.foods}, bodies: {my_snake_data.bodies}")
        print(f"reachable moves: {reachable}")
        # print(f"foods only you can reach: {board_data.foods_only_you_can_reach(my_snake_data, enemy_snake_data)}")
        print(f"MOVE {game_state['turn']}: {next_move_result}")
        # board_data.print_board()

    BoardData.previous_foods = board_data.foods.copy()
    
    return {"move": next_move_result}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
