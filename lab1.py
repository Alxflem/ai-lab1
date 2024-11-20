import tkinter as tk
from tkinter import messagebox
import numpy as np
import time

class OthelloGame:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)  # 0 = empty, 1 = black, -1 = white
        self.board[3, 3] = self.board[4, 4] = -1  # Initial white pieces
        self.board[3, 4] = self.board[4, 3] = 1   # Initial black pieces
        self.current_player = -1  # White starts

    def get_valid_moves(self, player):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        valid_moves = []

        for x in range(8):
            for y in range(8):
                if self.board[x, y] != 0:
                    continue

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    found_opponent = False

                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if self.board[nx, ny] == -player:
                            found_opponent = True
                        elif self.board[nx, ny] == player and found_opponent:
                            valid_moves.append((x, y))
                            break
                        else:
                            break

                        nx += dx
                        ny += dy

        return valid_moves

    def make_move(self, player, move):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        x, y = move
        self.board[x, y] = player

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            path = []

            while 0 <= nx < 8 and 0 <= ny < 8:
                if self.board[nx, ny] == -player:
                    path.append((nx, ny))
                elif self.board[nx, ny] == player:
                    for px, py in path:
                        self.board[px, py] = player
                    break
                else:
                    break

                nx += dx
                ny += dy

    def is_game_over(self):
        return not self.get_valid_moves(1) and not self.get_valid_moves(-1)

    def get_board_state(self):
        return self.board.copy()

    def reset(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.board[3, 3] = self.board[4, 4] = -1
        self.board[3, 4] = self.board[4, 3] = 1
        self.current_player = -1

class OthelloAI:
    def __init__(self, game):
        self.game = game
        self.max_depth = 4
        self.max_time = 5
        self.nodes_examined = 0

    def evaluate_board(self, board, player):
        """
        Basic evaluation function. 
        Override this method to implement your own strategy.
        """
        return np.sum(board == player) - np.sum(board == -player)

    def get_best_move(self, player):
        """
        Default AI move selection method. 
        Replace this with your own minimax/alpha-beta implementation.
        """
        start_time = time.time()
        self.nodes_examined = 0
        
        board_copy = self.game.get_board_state()
        best_move = None
        max_eval = -float('inf')
        
        valid_moves = self.game.get_valid_moves(player)
        
        for move in valid_moves:
            # Simulate the move
            game_copy = OthelloGame()
            game_copy.board = board_copy.copy()
            game_copy.make_move(player, move)
            
            # Evaluate the move
            move_eval = self.evaluate_board(game_copy.board, player)
            
            if move_eval > max_eval:
                max_eval = move_eval
                best_move = move
            
            self.nodes_examined += 1
            
            # Time check
            if time.time() - start_time > self.max_time:
                break
        
        return best_move, self.nodes_examined

class OthelloGUI:
    def __init__(self):
        self.game = OthelloGame()
        self.ai = OthelloAI(self.game)
        
        self.root = tk.Tk()
        self.root.title("Othello")
        self.create_gui()

    def create_gui(self):
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="green")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.info_label = tk.Label(self.root, text="White's turn", font=("Arial", 14))
        self.info_label.pack()

        self.reset_button = tk.Button(self.root, text="Reset Game", command=self.reset_game)
        self.reset_button.pack()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(9):
            self.canvas.create_line(0, i * 50, 400, i * 50, fill="black")
            self.canvas.create_line(i * 50, 0, i * 50, 400, fill="black")

        # Highlight valid moves
        valid_moves = self.game.get_valid_moves(self.game.current_player)
        for x, y in valid_moves:
            self.canvas.create_rectangle(
                y * 50, x * 50, y * 50 + 50, x * 50 + 50, 
                outline="blue", 
                width=3
            )

        # Draw discs
        board = self.game.get_board_state()
        for x in range(8):
            for y in range(8):
                if board[x, y] == 1:  # Black disc
                    self.canvas.create_oval(
                        y * 50 + 5, x * 50 + 5, y * 50 + 45, x * 50 + 45, fill="black"
                    )
                elif board[x, y] == -1:  # White disc
                    self.canvas.create_oval(
                        y * 50 + 5, x * 50 + 5, y * 50 + 45, x * 50 + 45, fill="white"
                    )

    def reset_game(self):
        self.game.reset()
        self.info_label.config(text="White's turn")
        self.draw_board()

    def handle_click(self, event):
        if self.game.current_player == 1:  # AI's turn
            return

        x, y = event.y // 50, event.x // 50

        valid_moves = self.game.get_valid_moves(self.game.current_player)
        if (x, y) in valid_moves:
            self.game.make_move(self.game.current_player, (x, y))
            self.game.current_player *= -1
            self.draw_board()

            if self.game.is_game_over():
                self.end_game()
            else:
                self.info_label.config(text="Black's turn (AI thinking...)")
                self.root.after(100, self.ai_turn)

    def ai_turn(self):
        best_move, nodes_examined = self.ai.get_best_move(self.game.current_player)
        
        if best_move:
            # Animate AI move
            self.animate_ai_move(best_move, nodes_examined)

    def animate_ai_move(self, move, nodes_examined):
        def highlight_move():
            x, y = move
            self.canvas.create_rectangle(
                y * 50, x * 50, y * 50 + 50, x * 50 + 50, 
                outline="red", 
                width=3
            )
            self.root.after(500, place_disc)

        def place_disc():
            self.game.make_move(self.game.current_player, move)
            self.game.current_player *= -1
            self.draw_board()

            # Print debug information
            print("Board after AI move:")
            print(self.game.get_board_state())
            print(f"Search Depth: {self.ai.max_depth}")
            print(f"Nodes Examined: {nodes_examined}\n")

            if self.game.is_game_over():
                self.end_game()
            else:
                self.info_label.config(text="White's turn")

        highlight_move()

    def end_game(self):
        board = self.game.get_board_state()
        black_score = np.sum(board == 1)
        white_score = np.sum(board == -1)
        winner = "Black" if black_score > white_score else "White" if white_score > black_score else "No one"
        messagebox.showinfo("Game Over", f"Game Over!\nBlack: {black_score}, White: {white_score}\nWinner: {winner}")
        self.reset_game()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = OthelloGUI()
    game.run()