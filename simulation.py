# import typing
# import random   
# from collections import deque
# from gamedata import SnakeData
# from reachable import Reachable

# class Simulation:
#     def __init__(self, game_data: SnakeData, max_depth: int) -> None:
#         #シミュレーション用データ
#         self.game_data = game_data
#         #最大の経路
#         self.max_depth = max_depth
#         #経路探索結果
#         self.result_tier1 = []
#         self.result_tier2 = []
#         self.result_tier3 = []
#         #長さが3〜4のときの探索済み経路保存用
#         self.dumped_route_34: typing.Dict[typing.Tuple[typing.Tuple[int, int], str], typing.Set[int]] = {}

#     #新版
#     def route_search(self, data: SnakeData, route: deque = deque()):
#         current_safes_around = data.safes_around()
#         current_head = data.head()
#         length = data.length()

#         #進行可能方向がない場合終了
#         if not current_safes_around:
#             return

#         #餌を食べたら経路を保存して終了
#         if data.head() in data.foods:
#             tail = data.tail()
#             data.bodies.append((-1, -1))
#             new_foods = data.foods.copy()
#             new_foods.remove(data.head())
#             if Reachable(bodies = data.bodies, foods = new_foods, width = SnakeData.board_width, height = SnakeData.board_height).is_reachable_food_avoidance(current_head, tail):
#                 copied_route = route.copy()
#                 self.result_tier1.append(copied_route)
#             elif Reachable(bodies = data.bodies, foods = new_foods, width = SnakeData.board_width, height = SnakeData.board_height).is_reachable(current_head, tail):
#                 copied_route = route.copy()
#                 self.result_tier2.append(copied_route)    
#             elif data.safes_around():
#                 copied_route = route.copy()
#                 self.result_tier3.append(copied_route)
#             data.bodies.pop()
#             return

#         #最大深度に達したら終了
#         if len(route) >= self.max_depth:
#             return

#         next = []
#         #長さが3〜4のときは全探索するが，頭の位置と首の向きが同じで体の長さも同じ場合は探索済みとして終了
#         if data.length() <= 4:
#             for move in current_safes_around:
#                 next_head = data.next_head_position(current_head, move)
#                 if (next_head, data.heading()) in self.dumped_route_34.keys():
#                     if data.length() in self.dumped_route_34[(next_head, data.heading())]:
#                         continue
#                     self.dumped_route_34[(next_head, data.heading())].add(data.length())
#                 else:
#                     self.dumped_route_34[(next_head, data.heading())] = set([data.length()])
#                 next.append(move)
#         else:
#             next = current_safes_around        
#         if 8 < length < 24 and len(next) > 2:
#             next = random.sample(next, 2)

#         for move in next:
#             current_head = data.head()
#             next_head = data.next_head_position(current_head, move)

#             # new_body = data.bodies.copy()
#             removed_tail = data.bodies.pop()
#             data.bodies.appendleft(next_head)
            
#             route.append(move)

#             data.generate_board()
#             self.route_search(data = data, route = route)

#             route.pop()
#             data.bodies.popleft()
#             data.bodies.append(removed_tail)
#             data.generate_board()