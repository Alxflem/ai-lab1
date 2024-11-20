import tkinter as tk
from tkinter import messagebox
import numpy as np
import time

class OthelloGUI:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)  # 0 = empty, 1 = black, -1 = white
        self.board[3, 3] = self.board[4, 4] = -1  # Initial white pieces
        self.board[3, 4] = self.board[4, 3] = 1   # Initial black pieces
        self.current_player = -1  # White starts
        self.max_depth = 4
        self.max_time = 5

        # Tracking number of nodes examined
        self.nodes_examined = 0

        # Create the main window
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
        valid_moves = self.get_valid_moves(self.current_player)
        for x, y in valid_moves:
            self.canvas.create_rectangle(
                y * 50, x * 50, y * 50 + 50, x * 50 + 50, 
                outline="blue", 
                width=3
            )

        # Draw discs
        for x in range(8):
            for y in range(8):
                if self.board[x, y] == 1:  # Black disc
                    self.canvas.create_oval(
                        y * 50 + 5, x * 50 + 5, y * 50 + 45, x * 50 + 45, fill="black"
                    )
                elif self.board[x, y] == -1:  # White disc
                    self.canvas.create_oval(
                        y * 50 + 5, x * 50 + 5, y * 50 + 45, x * 50 + 45, fill="white"
                    )

    def reset_game(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.board[3, 3] = self.board[4, 4] = -1
        self.board[3, 4] = self.board[4, 3] = 1
        self.current_player = -1
        self.nodes_examined = 0
        self.info_label.config(text="White's turn")
        self.draw_board()

    def handle_click(self, event):
        if self.current_player == 1:  # AI's turn
            return

        x, y = event.y // 50, event.x // 50

        valid_moves = self.get_valid_moves(self.current_player)
        if (x, y) in valid_moves:
            self.make_move(self.current_player, (x, y))
            self.current_player *= -1
            self.draw_board()

            if self.is_game_over():
                self.end_game()
            else:
                self.info_label.config(text="Black's turn (AI thinking...)")
                self.root.after(100, self.ai_turn)

    def ai_turn(self):
        start_time = time.time()
        self.nodes_examined = 0
        _, best_move = self.minimax(self.current_player, self.max_depth, -float("inf"), float("inf"), True, start_time, self.max_time)
        
        if best_move:
            # Animate AI move
            self.animate_ai_move(best_move)

    def animate_ai_move(self, move):
        def highlight_move():
            x, y = move
            self.canvas.create_rectangle(
                y * 50, x * 50, y * 50 + 50, x * 50 + 50, 
                outline="red", 
                width=3
            )
            self.root.after(500, place_disc)

        def place_disc():
            self.make_move(self.current_player, move)
            self.current_player *= -1
            self.draw_board()

            # Print debug information
            print("Board after AI move:")
            print(self.board)
            print(f"Search Depth: {self.max_depth}")
            print(f"Nodes Examined: {self.nodes_examined}\n")

            if self.is_game_over():
                self.end_game()
            else:
                self.info_label.config(text="White's turn")

        highlight_move()

    def end_game(self):
        black_score = np.sum(self.board == 1)
        white_score = np.sum(self.board == -1)
        winner = "Black" if black_score > white_score else "White" if white_score > black_score else "No one"
        messagebox.showinfo("Game Over", f"Game Over!\nBlack: {black_score}, White: {white_score}\nWinner: {winner}")
        self.reset_game()

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

    def evaluate_board(self, player):
        return np.sum(self.board == player) - np.sum(self.board == -player)

    def minimax(self, player, depth, alpha, beta, maximizing, start_time, max_time):
        if depth == 0 or self.is_game_over() or (time.time() - start_time) > max_time:
            return self.evaluate_board(player), None

        self.nodes_examined += 1  # Increment node count
        valid_moves = self.get_valid_moves(player if maximizing else -player)

        if not valid_moves:
            return self.minimax(player, depth - 1, alpha, beta, not maximizing, start_time, max_time)

        best_move = None

        if maximizing:
            max_eval = -float("inf")
            for move in valid_moves:
                board_copy = self.board.copy()
                self.make_move(player, move)
                eval, _ = self.minimax(player, depth - 1, alpha, beta, False, start_time, max_time)
                self.board = board_copy

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

            return max_eval, best_move

        else:
            min_eval = float("inf")
            for move in valid_moves:
                board_copy = self.board.copy()
                self.make_move(-player, move)
                eval, _ = self.minimax(player, depth - 1, alpha, beta, True, start_time, max_time)
                self.board = board_copy

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return min_eval, best_move

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = OthelloGUI()
    game.run()