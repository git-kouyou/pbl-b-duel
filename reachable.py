# from collections import deque
# from gamedata import Type, BoardData
# from gamedata import X as X
# from gamedata import Y as Y

# # 盤面表現: board[y][x]

# # BSFによる到達可能判定
# class Reachable:
#     def __init__(self, board_data: BoardData) -> None:
#         self.board = board_data.board

    
    
#     # デバッグ用盤面表示
#     def print_board(self):
#         for y in reversed(range(BoardData.height)):
#             row = ""
#             for x in range(BoardData.width):
#                 row += f"{self.board[y][x]}".rjust(2) + " "
#             print(row)
#         print()
    
# # デバッグ用
# if __name__ == "__main__":
#     DEBUG = True
#     foods = []
#     bodies = deque()
    
#     # BSF = Reachable()
#     # BSF.print_board()

#     # start = (0, 0)
#     # goal = (0, 0)

#     # print(f"reachable food avoid:{BSF.is_reachable_food_avoidance(start, goal)}")
#     # print(f"reachable:{BSF.is_reachable(start, goal)}")