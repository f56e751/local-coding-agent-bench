"""Go counting implementation."""

WHITE = 'W'
BLACK = 'B'
NONE = ''


class Board:
    """Count territories of each player in a Go game

    Args:
        board (list[str]): A two-dimensional Go board
    """

    def __init__(self, board):
        self.board = board
        self.height = len(board)
        self.width = len(board[0]) if board else 0

    def territory(self, x, y):
        """Find the owner and the territories given a coordinate on
           the board

        Args:
            x (int): Column on the board
            y (int): Row on the board

        Returns:
            (str, set): A tuple, the first element being the owner
                        of that area.  One of "W", "B", " ".  The
                        second being a set of coordinates, representing
                        the owner's territories.
        """
        # Validate coordinates
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            raise ValueError('Invalid coordinate')
        
        # If the position is not empty, return NONE with empty territory
        # We can't determine territory from a stone position
        if self.board[y][x] != ' ':
            return (NONE, set())
        
        # BFS to find all connected empty spaces (territory)
        visited = set()
        queue = [(x, y)]
        visited.add((x, y))
        territory = set()
        territory.add((x, y))
        
        # Track what stones border this territory
        borders = set()
        
        while queue:
            cx, cy = queue.pop(0)
            
            # Check all 4 adjacent positions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                
                # Check if neighbor is within bounds
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # If it's an empty space and not visited yet
                    if self.board[ny][nx] == ' ' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        territory.add((nx, ny))
                    # If it's a stone, it's a border
                    elif self.board[ny][nx] in [WHITE, BLACK]:
                        borders.add(self.board[ny][nx])
                else:
                    # Out of bounds - this counts as a border
                    borders.add(NONE)
        
        # Determine territory owner based on borders
        if len(borders) == 0:
            owner = NONE
        elif len(borders) == 1:
            owner = list(borders)[0]
        else:
            # Multiple borders - it's contested, so it's none
            owner = NONE
            
        return (owner, territory)

    def territories(self):
        """Find the owners and the territories of the whole board

        Args:
            none

        Returns:
            dict(str, set): A dictionary whose key being the owner
                        , i.e. "W", "B", " ".  The value being a set
                        of coordinates owned by the owner.
        """
        result = {BLACK: set(), WHITE: set(), NONE: set()}
        
        # Track all visited positions
        visited = set()
        
        for y in range(self.height):
            for x in range(self.width):
                # Only process empty positions
                if self.board[y][x] == ' ' and (x, y) not in visited:
                    # Find the territory starting from this position
                    stone, territory = self.territory(x, y)
                    # Mark all positions in this territory as visited
                    visited.update(territory)
                    # Add territory to the corresponding player's set
                    result[stone].update(territory)
                    
        return result