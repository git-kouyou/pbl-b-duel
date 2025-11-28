# 6班solo ソースコード
# python version: 3.13.3

import random
import typing
from reachable import Reachable
from gamedata import Status, GameData, Type
from simulation import Simulation

X = 0
Y = 1
MAX_DEPTH = 30

DEBUG = False

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
    GameData.initialized = False
    GameData(game_state)
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

def next_move(data: GameData) -> str:
    next_move = "None"
    safes_around = data.safes_around()

    #体が極小の時: 優先度1
    if data.length() <= 2:
        if data.no_foods():
            next_move = random.choice(data.no_foods())
        elif data.safes_around():
            next_move = random.choice(data.safes_around())
        return next_move

    # 指定ルートがある場合(エサを探すとき): 優先度2
    if GameData.isDisignated:
        if GameData.disignated_route:
            next_move = GameData.disignated_route.popleft()
            next_head = data.next_head_position(data.head(), next_move)

            if not (0 <= next_head[X] < GameData.board_width and 0 <= next_head[Y] < GameData.board_height and data.board[next_head[Y]][next_head[X]] <= Type.safe.value):
                #指定ルートが盤面外or安全でない場合，指定ルートを破棄してループ動作に戻る
                GameData.isDisignated = False
                GameData.status = Status.loop
                next_move = "None"
            else:
                if DEBUG:
                    print(f"Disignated Move: {next_move}")
                return next_move
        else:
            GameData.isDisignated = False
            GameData.status = Status.loop

    # 体力に応じたエサ探索開始長さの設定
    starting_length = 0
    if 3 <= data.length() <= 4:
        starting_length = 12
    elif data.length() <= 10:
        starting_length = 10
    elif data.length() <= 15:
        starting_length = 15
    elif data.length() <= 20:
        starting_length = 16
    elif data.length() <= 24:
        starting_length = 20
    elif data.length() <= 30:
        starting_length = 24
    else:
        starting_length = 30

    early_state = data.length() <= 10
    combat_moves = data.get_combat_moves()

    if not early_state and data.longer_than_opponent() and combat_moves["kill"]:
        next_move = random.choice(combat_moves["kill"])

        return next_move
    
    safes_after_combat = [m for m in data.safes_around() if m not in combat_moves["death"]]

    # エサ探索: 優先度3
    if early_state or data.shorter_than_opponent() or data.health <= starting_length:
        sorted_foods = sorted(list(data.foods), key = lambda f: abs(f[X] - data.head()[X]) + abs(f[Y] - data.head()[Y]))
        all_tier1 = []
        all_tier2 = []
        all_tier3 = []
        for food_target in sorted_foods:
            tmp_food = {food_target}

            simulator = Simulation(game_data = data, max_depth = min(data.health, MAX_DEPTH))
            original_foods = data.foods
            data.foods = tmp_food

            simulator.route_search(data = data)
            data.foods = original_foods
        
            if(simulator.result_tier1):
                all_tier1.extend(simulator.result_tier1)
            elif simulator.result_tier2:
                all_tier2.extend(simulator.result_tier2)
            elif simulator.result_tier3:
                all_tier3.extend(simulator.result_tier3)

        if all_tier1:
            GameData.disignated_route = max(all_tier1, key = len)
            print(f"Tire 1 route: {GameData.disignated_route}")
        elif all_tier2:
            GameData.disignated_route = max(all_tier2, key = len)
            print(f"Tire 2 route: {GameData.disignated_route}")
        elif all_tier3:
            GameData.disignated_route = max(all_tier3, key = len)
            print(f"Tire 3 route: {GameData.disignated_route}")

        if GameData.disignated_route:
            GameData.isDisignated = True
            GameData.status = Status.eat_food
            next_move = GameData.disignated_route.popleft()
            if DEBUG:
                print(f"Disignated Move: {next_move}")
            return next_move
        print("No route to food found!")

        if safes_after_combat:
            next_move = random.choice(safes_after_combat)
            return next_move
        
    # 進行可能方向がないor一つしかない場合の処理: 優先度4
    if not safes_around:
        if data.empty_around():
            next_move = random.choice(data.empty_around())
        else:
            if DEBUG:
                print("No safe move detected! move down!")
            next_move = "down"
        return next_move
    elif len(safes_around) == 1:
        if DEBUG:
            print("Only one safe move detected!")
        next_move = safes_around[0]
        return next_move

    # ループを探す動作: 優先度5
    if GameData.status == Status.loop:
        tier1 = []
        tier2 = []
        tier3 = []
        tier4 = []
        distance = {"up": data.tail()[Y] - data.head()[Y],
                    "down": data.head()[Y] - data.tail()[Y],
                    "right": data.tail()[X] - data.head()[X],
                    "left": data.head()[X] - data.tail()[X]}
        
        for move in safes_around:
            next_head = data.next_head_position(data.head(), move)
            new_body = data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if Reachable(bodies = new_body, foods = data.foods, width = GameData.board_width, height = GameData.board_height).is_reachable_food_avoidance(next_head, data.tail()):
                if distance[move] > 0:
                    tier1.append(move)
                else:
                    tier2.append(move)
            elif Reachable(bodies = new_body, foods = data.foods, width = GameData.board_width, height = GameData.board_height).is_reachable(next_head, data.tail()):
                if distance[move] > 0:
                    tier3.append(move)
                else:
                    tier4.append(move)
        if tier1:
            next_move = max(tier1, key = lambda m: distance[m])
        elif tier2:
            next_move = random.choice(tier2)
        elif tier3:
            next_move = max(tier3, key = lambda m: distance[m]) 
        elif tier4:
            next_move = random.choice(tier4)
        else:
            if data.heading() in data.no_foods():
                next_move = data.heading()
            elif data.no_foods():
                next_move = random.choice(data.no_foods())
    
    if next_move == "None":
        if safes_after_combat:
            next_move = random.choice(safes_after_combat)
        elif safes_around:
            next_move = random.choice(safes_around)

    return next_move

# 初期化やデバッグ表示など
def move(game_state: typing.Dict) -> typing.Dict:
    data = GameData(game_state)
    next_move_result = next_move(data)
    GameData.previous_foods = set(data.foods)
    
    reachable_food_avoidance = []
    reachable = []
    if data.length() >= 3:
        bsf = Reachable(bodies = data.bodies, foods = data.foods, width = GameData.board_width, height = GameData.board_height)
        for move in data.safes_around():
            next_head = data.next_head_position(data.head(), move)
            new_body = data.bodies.copy()
            new_body.pop()
            new_body.appendleft(next_head)
            if bsf.is_reachable_food_avoidance(next_head, data.tail()):
                reachable_food_avoidance.append(move)
            if bsf.is_reachable(next_head, data.tail()):
                reachable.append(move)

    if DEBUG:
        print(f"safes around: {data.safes_around()}, no_foods around: {data.no_foods()}")
        print(f"foods: {data.foods}, bodies: {data.bodies}")
        print(f"reachable: {reachable} reachable_food_avoidance: {reachable_food_avoidance}")
        print(f"MOVE {game_state['turn']}: {next_move_result}")
        print(f"status: {GameData.status}")
        data.print_board()
    return {"move": next_move_result}

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
