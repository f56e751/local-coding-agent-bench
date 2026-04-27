
class ConnectGame:
    def __init__(self, board):
        # Parse the board into a 2D list
        self.board = []
        for line in board.strip().split('\n'):
            row = []
            for char in line.strip():
                if char != ' ':
                    row.append(char)
            if row:
                self.board.append(row)
        
        self.rows = len(self.board)
        self.cols = len(self.board[0]) if self.board else 0

    def get_winner(self):
        # Check if X (left to right) wins
        if self._is_connected('X'):
            return 'X'
        
        # Check if O (top to bottom) wins
        if self._is_connected('O'):
            return 'O'
            
        return ''

    def _is_connected(self, player):
        """Check if player has formed a connected path from start to end"""
        if player == 'X':
            # X connects left to right
            # Start from leftmost column and do BFS/DFS to rightmost column
            visited = set()
            # Find all starting positions on left edge
            for row in range(self.rows):
                if self.board[row][0] == player:
                    if self._dfs_x(row, 0, visited):
                        return True
            return False
        else:
            # O connects top to bottom
            # Start from top row and do BFS/DFS to bottom row
            visited = set()
            # Find all starting positions on top edge
            for col in range(self.cols):
                if self.board[0][col] == player:
                    if self._dfs_o(0, col, visited):
                        return True
            return False

    def _dfs_x(self, row, col, visited):
        """Depth-first search for X connecting left to right"""
        # If we've reached the right edge, X wins
        if col == self.cols - 1:
            return True
            
        # Mark current position as visited
        visited.add((row, col))
        
        # Check all 6 adjacent positions (hexagonal grid)
        # For a hex grid with axial coordinates, neighbors are:
        # (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col)
        neighbors = [
            (row-1, col),      # up
            (row-1, col+1),     # up-right
            (row, col-1),       # left
            (row, col+1),       # right
            (row+1, col-1),     # down-left
            (row+1, col)        # down
        ]
        
        for n_row, n_col in neighbors:
            # Check if neighbor is valid and unvisited and has the correct player
            if (0 <= n_row < self.rows and 
                0 <= n_col < self.cols and 
                (n_row, n_col) not in visited and
                self.board[n_row][n_col] == 'X'):
                if self._dfs_x(n_row, n_col, visited):
                    return True
        
        return False

    def _dfs_o(self, row, col, visited):
        """Depth-first search for O connecting top to bottom"""
        # If we've reached the bottom edge, O wins
        if row == self.rows - 1:
            return True
            
        # Mark current position as visited
        visited.add((row, col))
        
        # Check all 6 adjacent positions
        neighbors = [
            (row-1, col),      # up
            (row-1, col+1),     # up-right
            (row, col-1),       # left
            (row, col+1),       # right
            (row+1, col-1),     # down-left
            (row+1, col)        # down
        ]
        
        for n_row, n_col in neighbors:
            # Check if neighbor is valid and unvisited and has the correct player
            if (0 <= n_row < self.rows and 
                0 <= n_col < self.cols and 
                (n_row, n_col) not in visited and
                self.board[n_row][n_col] == 'O'):
                if self._dfs_o(n_row, n_col, visited):
                    return True
        
        return False
