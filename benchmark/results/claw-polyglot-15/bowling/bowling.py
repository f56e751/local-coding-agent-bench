class BowlingGame:
    def __init__(self):
        self.rolls = []
        
    def roll(self, pins):
        if pins < 0:
            raise ValueError("cannot roll negative pins")
        if pins > 10:
            raise ValueError("cannot roll more than 10 pins")
            
        self.rolls.append(pins)
        
        # Game can be at most 21 rolls (9 frames * 2 rolls + 3 bonus rolls maximum)
        if len(self.rolls) > 21:
            raise IndexError("cannot roll after game is complete")
            
        # Validate 10th frame rules (when we have 18 or more rolls)
        if len(self.rolls) >= 18:
            tenth_frame_rolls = self.rolls[18:]
            
            # For 2 rolls in 10th frame, we check validity (unless it's a strike)
            if len(tenth_frame_rolls) == 2:
                if tenth_frame_rolls[0] != 10 and (tenth_frame_rolls[0] + tenth_frame_rolls[1]) > 10:
                    raise ValueError("cannot roll more than 10 pins in 10th frame")
            
            # For 3 rolls in 10th frame:
            elif len(tenth_frame_rolls) == 3:
                if tenth_frame_rolls[0] == 10:
                    # First is strike, validate second and third
                    if tenth_frame_rolls[1] < 10 and (tenth_frame_rolls[1] + tenth_frame_rolls[2]) > 10:
                        raise ValueError("cannot roll more than 10 pins in 10th frame")
                else:
                    # First is not strike but we have 3 rolls; this should not happen in valid games
                    if tenth_frame_rolls[0] + tenth_frame_rolls[1] > 10:
                        raise ValueError("cannot roll more than 10 pins in 10th frame")
            
    def score(self):
        if not self.rolls:
            raise IndexError("cannot score empty game")
            
        # At least 18 rolls must be completed
        if len(self.rolls) < 18:
            raise IndexError("cannot score incomplete game")
            
        # Check if 10th frame is complete  
        tenth_frame_rolls = self.rolls[18:]
        
        # Cannot score if 10th frame is incomplete (has only 1 roll)
        if len(tenth_frame_rolls) == 1:
            raise IndexError("cannot score incomplete game")
            
        # For 10th frame with 2 rolls:
        # If strike (first is 10), must have 20 rolls to be complete
        # If spare, must have 20 rolls to be complete
        if len(tenth_frame_rolls) == 2:
            if tenth_frame_rolls[0] == 10:
                if len(self.rolls) < 20:
                    raise IndexError("cannot score incomplete game")
            elif tenth_frame_rolls[0] + tenth_frame_rolls[1] == 10:
                if len(self.rolls) < 20:
                    raise IndexError("cannot score incomplete game")
                    
        total = 0
        roll_index = 0
        
        # Process 10 frames
        for frame in range(10):
            if roll_index >= len(self.rolls):
                break
                
            if frame < 9:  # Regular frames 1-9
                first_roll = self.rolls[roll_index]
                
                if first_roll == 10:  # Strike
                    total += 10
                    # Bonus: next two rolls
                    if roll_index + 1 < len(self.rolls):
                        bonus = self.rolls[roll_index + 1]
                        if roll_index + 2 < len(self.rolls):
                            bonus += self.rolls[roll_index + 2]
                        total += bonus
                    roll_index += 1  # 1 roll used for strike
                else:
                    # Open or spare
                    second_roll = self.rolls[roll_index + 1]
                    if first_roll + second_roll > 10:
                        raise ValueError("cannot roll more than 10 pins in a frame")
                    total += first_roll + second_roll
                    if first_roll + second_roll == 10:  # Spare
                        # Bonus: next roll
                        if roll_index + 2 < len(self.rolls):
                            total += self.rolls[roll_index + 2]
                    roll_index += 2  # 2 rolls used for this frame
            else:  # Tenth frame (frame 10)
                # Process 10th frame
                if len(self.rolls) >= 20:
                    # 10th frame has 2 rolls plus possibly a 3rd bonus roll
                    total += self.rolls[18] + self.rolls[19]
                    if len(self.rolls) == 21:
                        # Add the third roll (bonus)
                        total += self.rolls[20]
                else:
                    # Only 19 rolls - no bonus roll (this can happen with 19 rolls)
                    total += self.rolls[18] + self.rolls[19]
                break
                
        return total